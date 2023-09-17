import os
import shutil
import hashlib
import time
import logging
from pathlib import Path

def count_files_in_directory(directory):
    count = 0
    for _ in Path(directory).rglob('*'):
        if _.is_file():
            count += 1
    return count

def copy_files_with_duplicates(source_folder, destination_folder):
    # Create a logger
    logger = logging.getLogger('file_copy')
    logger.setLevel(logging.DEBUG)

    # Create a file handler for the logger
    file_handler = logging.FileHandler('file_copy3.log')
    file_handler.setLevel(logging.DEBUG)

    # Create a console handler for the logger
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    total_files_processed = 0
    total_bytes_processed = 0
    total_files_skipped = 0

    start_time = time.time()

    # Count total files to process
    total_files_to_process = count_files_in_directory(source_folder)

    for source_file_path in Path(source_folder).rglob('*'):
        if not source_file_path.is_file():
            continue

        relative_path = source_file_path.relative_to(source_folder)
        destination_file_path = Path(destination_folder) / relative_path

        try:
            if not destination_file_path.exists():
                destination_file_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(source_file_path), str(destination_file_path))
                total_files_processed += 1
                file_size_mb = source_file_path.stat().st_size / (1024 * 1024)
                total_bytes_processed += source_file_path.stat().st_size
                logger.info(f"Copied: {relative_path} ({file_size_mb:.2f} MB)")
            else:
                source_file_checksum = hashlib.md5(source_file_path.read_bytes()).hexdigest()
                destination_file_checksum = hashlib.md5(destination_file_path.read_bytes()).hexdigest()

                if source_file_checksum == destination_file_checksum:
                    total_files_skipped += 1
                    logger.info(f"Skipping duplicate: {relative_path}")
                else:
                    shutil.copy2(str(source_file_path), str(destination_file_path))
                    total_files_processed += 1
                    file_size_mb = source_file_path.stat().st_size / (1024 * 1024)
                    total_bytes_processed += source_file_path.stat().st_size
                    logger.info(f"Copying modified version: {relative_path} ({file_size_mb:.2f} MB)")
        except Exception as e:
            logger.error(f"Error copying {relative_path}: {e}")

        # Calculate progress
        elapsed_time = time.time() - start_time
        percent_complete = (total_files_processed / total_files_to_process) * 100

        logger.info(f"Progress: {total_files_processed} / {total_files_to_process} files "
                    f"({percent_complete:.2f}% complete), "
                    f"Total data processed: {total_bytes_processed / (1024 * 1024):.2f} MB, "
                    f"Elapsed time: {elapsed_time:.2f} seconds.")

    end_time = time.time()
    elapsed_time = end_time - start_time

    logger.info(f"Processed {total_files_processed} of {total_files_to_process} files.")
    logger.info(f"Total data processed: {total_bytes_processed / (1024 * 1024):.2f} MB.")
    logger.info(f"Elapsed time: {elapsed_time:.2f} seconds.")
    logger.info(f"Total files skipped: {total_files_skipped}")

if __name__ == "__main__":
    # Define source and destination folders
    source_folder = r"G:\My Drive\JMU"
    destination_folder = r"C:\Users\karl_\Downloads\JMU"
    copy_files_with_duplicates(source_folder, destination_folder)
