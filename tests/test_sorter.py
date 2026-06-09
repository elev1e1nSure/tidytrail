"""Comprehensive tests for sorter.py with 100% coverage."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call
import shutil

from src.sorter import plan_sort, execute_sort, _generate_unique_name, _get_category_for_file
from src.models import FileInfo, ScanResult
from src.config import Category


class TestGenerateUniqueName:
    """Test _generate_unique_name function."""

    def test_no_collision_returns_original(self, tmp_path):
        """When no collision exists, return original filename."""
        result = _generate_unique_name(tmp_path, "file.txt")
        assert result == tmp_path / "file.txt"
        assert result.name == "file.txt"

    def test_single_collision_adds_counter_1(self, tmp_path):
        """When collision exists, add _1 suffix."""
        (tmp_path / "file.txt").touch()
        result = _generate_unique_name(tmp_path, "file.txt")
        assert result == tmp_path / "file_1.txt"
        assert result.name == "file_1.txt"

    def test_multiple_collisions_increments_counter(self, tmp_path):
        """When multiple collisions exist, increment counter until unique."""
        (tmp_path / "file.txt").touch()
        (tmp_path / "file_1.txt").touch()
        (tmp_path / "file_2.txt").touch()
        result = _generate_unique_name(tmp_path, "file.txt")
        assert result == tmp_path / "file_3.txt"
        assert result.name == "file_3.txt"

    def test_preserves_extension(self, tmp_path):
        """Ensure extension is preserved in generated name."""
        (tmp_path / "document.pdf").touch()
        result = _generate_unique_name(tmp_path, "document.pdf")
        assert result.suffix == ".pdf"
        assert result.stem == "document_1"

    def test_handles_files_without_extension(self, tmp_path):
        """Handle files without extension correctly."""
        (tmp_path / "README").touch()
        result = _generate_unique_name(tmp_path, "README")
        assert result.suffix == ""
        assert result.stem == "README_1"

    def test_handles_multiple_dots_in_filename(self, tmp_path):
        """Handle filenames with multiple dots correctly."""
        (tmp_path / "archive.tar.gz").touch()
        result = _generate_unique_name(tmp_path, "archive.tar.gz")
        assert result.name == "archive.tar_1.gz"

    def test_returns_path_object(self, tmp_path):
        """Ensure return type is Path object."""
        result = _generate_unique_name(tmp_path, "test.txt")
        assert isinstance(result, Path)


class TestGetCategoryForFile:
    """Test _get_category_for_file function."""

    @patch("src.sorter.get_category")
    def test_calls_get_category_with_file_path(self, mock_get_category):
        """Verify get_category is called with file path."""
        file_info = FileInfo(path=Path("/test/file.txt"), size=100, mtime=123.0)
        mock_get_category.return_value = Category.DOCS
        
        result = _get_category_for_file(file_info)
        
        mock_get_category.assert_called_once_with(file_info.path)
        assert result == Category.DOCS

    @patch("src.sorter.get_category")
    def test_returns_category_from_get_category(self, mock_get_category):
        """Verify category is returned correctly."""
        file_info = FileInfo(path=Path("/test/image.jpg"), size=200, mtime=124.0)
        mock_get_category.return_value = Category.IMAGES
        
        result = _get_category_for_file(file_info)
        
        assert result == Category.IMAGES


class TestPlanSort:
    """Test plan_sort function."""

    def test_empty_scan_returns_empty_plan(self):
        """When scan has no files, return empty plan."""
        scan = ScanResult(files=[], categories={})
        plan = plan_sort(scan, Path("/target"))
        assert plan == {}

    def test_skips_directories(self, tmp_path):
        """When file is a directory, skip it."""
        dir_path = tmp_path / "test_dir"
        dir_path.mkdir()
        scan = ScanResult(files=[
            FileInfo(path=dir_path, size=0, mtime=123.0),
        ], categories={})
        plan = plan_sort(scan, Path("/target"))
        assert plan == {}

    @patch("src.sorter.get_category")
    def test_skips_other_category(self, mock_get_category):
        """When category is OTHER, skip the file."""
        mock_get_category.return_value = Category.OTHER
        scan = ScanResult(files=[
            FileInfo(path=Path("/test/file.txt"), size=100, mtime=123.0),
        ], categories={})
        plan = plan_sort(scan, Path("/target"))
        assert plan == {}

    @patch("src.sorter.get_category")
    def test_creates_plan_for_valid_file(self, mock_get_category):
        """When file has valid category, add to plan."""
        mock_get_category.return_value = Category.IMAGES
        scan = ScanResult(files=[
            FileInfo(path=Path("/test/photo.jpg"), size=100, mtime=123.0),
        ], categories={})
        plan = plan_sort(scan, Path("/target"))
        
        assert Path("/test/photo.jpg") in plan
        assert plan[Path("/test/photo.jpg")] == Path("/target/images/photo.jpg")

    @patch("src.sorter.get_category")
    def test_handles_multiple_files(self, mock_get_category):
        """When multiple files, create plan for all valid ones."""
        mock_get_category.side_effect = [Category.IMAGES, Category.DOCS, Category.OTHER]
        scan = ScanResult(files=[
            FileInfo(path=Path("/test/photo.jpg"), size=100, mtime=123.0),
            FileInfo(path=Path("/test/doc.pdf"), size=200, mtime=124.0),
            FileInfo(path=Path("/test/unknown.xyz"), size=50, mtime=125.0),
        ], categories={})
        plan = plan_sort(scan, Path("/target"))
        
        assert len(plan) == 2
        assert Path("/test/photo.jpg") in plan
        assert Path("/test/doc.pdf") in plan
        assert Path("/test/unknown.xyz") not in plan

    @patch("src.sorter.get_category")
    def test_uses_category_value_for_subdirectory(self, mock_get_category):
        """Verify category value is used for subdirectory."""
        mock_get_category.return_value = Category.VIDEO
        scan = ScanResult(files=[
            FileInfo(path=Path("/test/movie.mp4"), size=500, mtime=123.0),
        ], categories={})
        plan = plan_sort(scan, Path("/target"))
        
        assert plan[Path("/test/movie.mp4")].parent == Path("/target/video")

    @patch("src.sorter.get_category")
    @patch("src.sorter._generate_unique_name")
    def test_calls_generate_unique_name(self, mock_gen_name, mock_get_category, tmp_path):
        """Verify _generate_unique_name is called for each file."""
        mock_get_category.return_value = Category.CODE
        mock_gen_name.return_value = tmp_path / "script.py"
        scan = ScanResult(files=[
            FileInfo(path=Path("/test/script.py"), size=100, mtime=123.0),
        ], categories={})
        
        plan_sort(scan, Path("/target"))
        
        mock_gen_name.assert_called_once()


class TestExecuteSort:
    """Test execute_sort function."""

    @patch("src.sorter.log_sort_operation")
    @patch("src.sorter.shutil.move")
    @patch("src.sorter.get_logger")
    def test_dry_run_skips_move_and_log(self, mock_logger, mock_move, mock_log):
        """When dry_run is True, skip actual move and log operation."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        plan = {Path("/src/file.txt"): Path("/dest/file.txt")}
        
        moved, skipped = execute_sort(plan, dry_run=True)
        
        mock_move.assert_not_called()
        mock_log.assert_not_called()
        mock_logger_instance.info.assert_called()
        assert moved == 1
        assert skipped == 0

    @patch("src.sorter.log_sort_operation")
    @patch("src.sorter.shutil.move")
    @patch("src.sorter.get_logger")
    def test_normal_run_moves_files_and_logs(self, mock_logger, mock_move, mock_log):
        """When dry_run is False, move files and log operation."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        plan = {Path("/src/file.txt"): Path("/dest/file.txt")}
        
        moved, skipped = execute_sort(plan, dry_run=False)
        
        mock_move.assert_called_once_with(str(Path("/src/file.txt")), str(Path("/dest/file.txt")))
        mock_log.assert_called_once_with(Path("/src/file.txt"), Path("/dest/file.txt"))
        assert moved == 1
        assert skipped == 0

    @patch("src.sorter.log_sort_operation")
    @patch("src.sorter.shutil.move")
    @patch("src.sorter.get_logger")
    def test_creates_parent_directories(self, mock_logger, mock_move, mock_log, tmp_path):
        """Verify parent directories are created."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        dest = tmp_path / "subdir" / "file.txt"
        plan = {Path("/src/file.txt"): dest}
        
        execute_sort(plan, dry_run=False)
        
        assert dest.parent.exists()

    @patch("src.sorter.log_sort_operation")
    @patch("src.sorter.shutil.move")
    @patch("src.sorter.get_logger")
    def test_permission_error_increments_skipped(self, mock_logger, mock_move, mock_log):
        """When PermissionError occurs, increment skipped count."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        mock_move.side_effect = PermissionError("Access denied")
        plan = {Path("/src/file.txt"): Path("/dest/file.txt")}
        
        moved, skipped = execute_sort(plan, dry_run=False)
        
        assert moved == 0
        assert skipped == 1
        mock_logger_instance.warning.assert_called()

    @patch("src.sorter.log_sort_operation")
    @patch("src.sorter.shutil.move")
    @patch("src.sorter.get_logger")
    def test_os_error_increments_skipped(self, mock_logger, mock_move, mock_log):
        """When OSError occurs, increment skipped count."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        mock_move.side_effect = OSError("Disk full")
        plan = {Path("/src/file.txt"): Path("/dest/file.txt")}
        
        moved, skipped = execute_sort(plan, dry_run=False)
        
        assert moved == 0
        assert skipped == 1
        mock_logger_instance.warning.assert_called()

    @patch("src.sorter.log_sort_operation")
    @patch("src.sorter.shutil.move")
    @patch("src.sorter.get_logger")
    def test_handles_mixed_success_and_failure(self, mock_logger, mock_move, mock_log):
        """When some files fail, count correctly."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        mock_move.side_effect = [None, PermissionError("Error"), None]
        plan = {
            Path("/src/file1.txt"): Path("/dest/file1.txt"),
            Path("/src/file2.txt"): Path("/dest/file2.txt"),
            Path("/src/file3.txt"): Path("/dest/file3.txt"),
        }
        
        moved, skipped = execute_sort(plan, dry_run=False)
        
        assert moved == 2
        assert skipped == 1

    @patch("src.sorter.log_sort_operation")
    @patch("src.sorter.shutil.move")
    @patch("src.sorter.get_logger")
    def test_empty_plan_returns_zero_counts(self, mock_logger, mock_move, mock_log):
        """When plan is empty, return (0, 0)."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        
        moved, skipped = execute_sort({}, dry_run=False)
        
        assert moved == 0
        assert skipped == 0
        mock_move.assert_not_called()

    @patch("src.sorter.log_sort_operation")
    @patch("src.sorter.shutil.move")
    @patch("src.sorter.get_logger")
    def test_logs_info_on_successful_move(self, mock_logger, mock_move, mock_log):
        """Verify info log is called on successful move."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        plan = {Path("/src/file.txt"): Path("/dest/file.txt")}
        
        execute_sort(plan, dry_run=False)
        
        assert mock_logger_instance.info.call_count >= 1

    @patch("src.sorter.log_sort_operation")
    @patch("src.sorter.shutil.move")
    @patch("src.sorter.get_logger")
    def test_logs_warning_on_failure(self, mock_logger, mock_move, mock_log):
        """Verify warning log is called on failure."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        mock_move.side_effect = PermissionError("Error")
        plan = {Path("/src/file.txt"): Path("/dest/file.txt")}
        
        execute_sort(plan, dry_run=False)
        
        mock_logger_instance.warning.assert_called()
        assert "Failed to move" in str(mock_logger_instance.warning.call_args)

    @patch("src.sorter.log_sort_operation")
    @patch("src.sorter.shutil.move")
    @patch("src.sorter.get_logger")
    def test_progress_bar_is_used(self, mock_logger, mock_move, mock_log):
        """Verify progress bar is created and updated."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        plan = {Path("/src/file.txt"): Path("/dest/file.txt")}
        
        with patch("src.sorter.Progress") as mock_progress:
            mock_progress_instance = MagicMock()
            mock_progress.return_value.__enter__.return_value = mock_progress_instance
            mock_progress_instance.add_task.return_value = "task_id"
            
            execute_sort(plan, dry_run=False)
            
            mock_progress.assert_called_once()
            mock_progress_instance.add_task.assert_called_once()
            mock_progress_instance.advance.assert_called_once()
