import os
import argparse
from os.path import exists

from moviepy.editor import VideoFileClip
from moviepy.tools import cvsecs, subprocess_call
from moviepy.video.tools.cuts import FramesMatches


def parse_arguments():
    parser = argparse.ArgumentParser(description="Tail wag generation")
    parser.add_argument("video", nargs="+",
                        help="The video(s) to be scanned and giffed"
                        )
    parser.add_argument("--outdir", type=str, default=os.getcwd(),
                        help="Base folder for gif output (cwd is default)"
                        )
    parser.add_argument("--time_start", default=None,
                        help="Start time for GIF scanning (Default: start of file)"
                        )
    parser.add_argument("--time_end", default=None,
                        help="End time for GIF scanning (Default: end of file)"
                        )
    parser.add_argument("--dist_thr", type=int, default=10,
                        help="[FramesMatches.from_clip] Distance above which a match is rejected (Default: 10)"
                        )
    parser.add_argument("--max_d", type=int, default=4,
                        help="[FramesMatches.from_clip] Maximal duration (in seconds) between two matching frames"
                             " (Default: 4)"
                        )
    parser.add_argument("--match_thr", type=int, default=2,
                        help="[FramesMatches.select_scenes] The smaller, the better-looping the gifs are. (Default: 2)"
                        )
    parser.add_argument("--min_time_span", type=float, default=1,
                        help="[FramesMatches.select_scenes] Minimum GIF length to extract (Default: 1s)"
                        )
    parser.add_argument("--nomatch_thr", type=int, default=4,
                        help="[FramesMatches.select_scenes] If None, then it is chosen equal to match_thr (Default: 4)"
                        )
    parser.add_argument("--time_distance", type=float, default=0.5,
                        help="[FramesMatches.select_scenes] Minimum distance from previous start time (Default: 0.5)"
                        )
    return parser.parse_args()


def optimize_gif(path, file):
    image_magick = os.getenv("MAGICK_PATH")

    base_name = os.path.splitext(os.path.basename(file))[0]

    cmd = [
        image_magick,
        "convert",
        os.path.join(path, file),
        "-layers",
        "coalesce",
        "-fuzz",
        "25%",
        "-layers",
        "remove-dups",
        "+delete",
        os.path.join(path, f"{base_name}.optimized.gif")
    ]
    subprocess_call(cmd)


def optimize_dir(path):
    image_magick = os.getenv("MAGICK_PATH")
    if image_magick is None:
        return

    files = os.listdir(path)
    for gif in files:
        if gif.endswith("optimized.gif"):
            continue
        if gif.endswith(".gif"):
            optimize_gif(path, gif)


def process_vid(video, args):
    """
    If video is not valid we will print error and pass
    out_directory must exist!
    """

    out_directory = get_output_directory(args.outdir, video, args)

    try:
        clip = VideoFileClip(video)
    except Exception as e:
        print(f"Unable to open clip{video}: {e}")
        return

    save_file = get_save_file(out_directory, video, args)
    if args.time_start is not None:
        clip = clip.subclip(t_start=args.time_start, t_end=args.time_end)

    if exists(save_file):
        scenes = FramesMatches.load(save_file)
    else:
        scenes = FramesMatches.from_clip(clip.resize(width=120), dist_thr=args.dist_thr, max_d=args.max_d)
        try:
            scenes.save(save_file)
        except Exception as e:
            print(f"Unable to save matches: {e}")

    selected_scenes = scenes.select_scenes(match_thr=args.match_thr, min_time_span=args.min_time_span,
                                           nomatch_thr=args.nomatch_thr, time_distance=args.time_distance)
    selected_scenes.write_gifs(clip.resize(width=450), out_directory)
    optimize_dir(out_directory)


def get_save_file(outdir, video, args):
    base_filename = os.path.basename(video)
    save_file = f"{base_filename}.{args.dist_thr}.{args.max_d}"
    if args.time_start is not None:
        save_file += f".{cvsecs(args.time_start)}-{cvsecs(args.time_end)}"
    save_file += ".framematches.txt"

    return os.path.join(outdir, save_file)


def get_output_directory(basedir, video, args):
    base_filename = os.path.splitext(os.path.basename(video))[0]
    if args.time_start is not None:
        if args.time_end is not None:
            base_filename += f" ({cvsecs(args.time_start)}-{cvsecs(args.time_end)})"
    outdir = os.path.join(basedir, base_filename)
    try:
        os.mkdir(outdir)
    except OSError:
        pass
    return outdir


if __name__ == '__main__':
    args = parse_arguments()
    for video in args.video:
        name = os.path.basename(video)
        print(f"~ Processing: {name}")
        process_vid(video, args)
