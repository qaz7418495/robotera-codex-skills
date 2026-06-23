#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mcap.reader import make_reader


def fmt_time(ns: int, tz_hours: int) -> str:
    tz = timezone(timedelta(hours=tz_hours))
    return datetime.fromtimestamp(ns / 1e9, tz).isoformat(timespec="milliseconds")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize ROS2 MCAP topics.")
    parser.add_argument("mcap", type=Path)
    parser.add_argument("--tz-hours", type=int, default=8)
    args = parser.parse_args()

    with args.mcap.open("rb") as f:
        reader = make_reader(f)
        summary = reader.get_summary()
        stats = summary.statistics
        duration = (stats.message_end_time - stats.message_start_time) / 1e9

        print(f"file,{args.mcap}")
        print(f"size_bytes,{args.mcap.stat().st_size}")
        print(f"message_count,{stats.message_count}")
        print(f"duration_s,{duration:.3f}")
        print(f"start_local,{fmt_time(stats.message_start_time, args.tz_hours)}")
        print(f"end_local,{fmt_time(stats.message_end_time, args.tz_hours)}")
        print()
        print("channel_id,topic,type,message_encoding,schema_encoding,count,avg_hz")
        for channel_id, channel in sorted(summary.channels.items()):
            schema = summary.schemas.get(channel.schema_id)
            count = stats.channel_message_counts.get(channel_id, 0)
            hz = count / duration if duration > 0 else 0
            print(
                f"{channel_id},{channel.topic},{schema.name if schema else ''},"
                f"{channel.message_encoding},{schema.encoding if schema else ''},"
                f"{count},{hz:.3f}"
            )


if __name__ == "__main__":
    main()
