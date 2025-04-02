#!/usr/bin/env python3
"""
Content Pipeline Scheduler

This script sets up automatic scheduling for the content generation pipeline.
It can be used to run the pipeline at regular intervals or on a specific schedule.

Usage:
  python schedule_pipeline.py --interval 30 --units minutes
  python schedule_pipeline.py --interval 1 --units days --at "10:00"
"""

import os
import sys
import time
import argparse
import logging
import schedule
import subprocess
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline_scheduler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("PipelineScheduler")

def run_pipeline(config_file=None, output_dir=None, num_stories=1):
    """
    Run the content generation pipeline.
    
    Args:
        config_file (str, optional): Path to configuration file
        output_dir (str, optional): Output directory for generated content
        num_stories (int): Number of stories to generate
    """
    logger.info(f"Running content pipeline: {num_stories} stories")
    
    cmd = ["python", "automated_content_pipeline.py", f"--num-stories={num_stories}"]
    
    if config_file:
        cmd.append(f"--config={config_file}")
    
    if output_dir:
        cmd.append(f"--output-dir={output_dir}")
    
    try:
        logger.info(f"Executing: {' '.join(cmd)}")
        process = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Pipeline execution successful: {process.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Pipeline execution failed: {e}")
        logger.error(f"Error output: {e.stderr}")
    except Exception as e:
        logger.error(f"Failed to run pipeline: {e}")

def format_next_run(job):
    """
    Format the next run time for a scheduled job.
    
    Args:
        job: The scheduled job
        
    Returns:
        str: Formatted next run time
    """
    next_run = job.next_run
    if next_run:
        return next_run.strftime("%Y-%m-%d %H:%M:%S")
    return "Not scheduled"

def main():
    """
    Main function to set up the scheduler.
    """
    parser = argparse.ArgumentParser(description="Content Pipeline Scheduler")
    parser.add_argument("--interval", type=int, default=1, help="Interval between runs")
    parser.add_argument("--units", choices=["minutes", "hours", "days"], default="days", help="Time units for interval")
    parser.add_argument("--at", help="Time of day to run (HH:MM format, for daily schedules)")
    parser.add_argument("--config", help="Path to pipeline configuration file")
    parser.add_argument("--output-dir", default="generated_content", help="Output directory for generated content")
    parser.add_argument("--num-stories", type=int, default=1, help="Number of stories to generate per run")
    parser.add_argument("--run-now", action="store_true", help="Run the pipeline immediately")
    
    args = parser.parse_args()
    
    # Set up the job with the appropriate arguments
    job_kwargs = {
        "config_file": args.config,
        "output_dir": args.output_dir,
        "num_stories": args.num_stories
    }
    
    # Set up the schedule based on the specified interval and units
    if args.units == "minutes":
        if args.interval < 1:
            logger.error("Interval must be at least 1 minute")
            return 1
        job = schedule.every(args.interval).minutes.do(run_pipeline, **job_kwargs)
        
    elif args.units == "hours":
        if args.interval < 1:
            logger.error("Interval must be at least 1 hour")
            return 1
        job = schedule.every(args.interval).hours.do(run_pipeline, **job_kwargs)
        
    elif args.units == "days":
        if args.interval < 1:
            logger.error("Interval must be at least 1 day")
            return 1
        
        if args.at:
            try:
                hour, minute = map(int, args.at.split(':'))
                job = schedule.every(args.interval).days.at(args.at).do(run_pipeline, **job_kwargs)
            except ValueError:
                logger.error(f"Invalid time format: {args.at}. Please use HH:MM format.")
                return 1
        else:
            job = schedule.every(args.interval).days.do(run_pipeline, **job_kwargs)
    
    # Print schedule information
    next_run = format_next_run(job)
    logger.info(f"Pipeline scheduled to run every {args.interval} {args.units}")
    logger.info(f"Next run: {next_run}")
    
    # Run immediately if requested
    if args.run_now:
        logger.info("Running pipeline now as requested")
        run_pipeline(**job_kwargs)
    
    # Keep the script running and execute scheduled jobs
    try:
        logger.info("Scheduler started. Press Ctrl+C to exit.")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check for pending jobs every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())