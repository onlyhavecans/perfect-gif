import os
import argparse
from moviepy.editor import VideoFileClip
from moviepy.video.tools.cuts import FramesMatches


def parse_arguments():
    parser = argparse.ArgumentParser(description="Tail wag generation")
    parser.add_argument("video", nargs="+",
                        help="The video(s) to be scanned and giffed"
                        )
    parser.add_argument("--outdir", nargs=1, default=[os.getcwd()],
                        help="Base folder for gif output (cwd is default)"
                        )
    return parser.parse_args()


def process_vid(video, out_directory):
    """
    If video is not valid we will print error and pass
    out_directory must exist!
    """
    try:
        clip = VideoFileClip(video).resize(width=120)
        scenes = FramesMatches.from_clip(clip, dist_thr=10, max_d=4)
    except Exception:
        print("oops, Looks like {} isn't a vid".format(video))
        return
    selected_scenes = scenes.select_scenes(match_thr=2, min_time_span=1, nomatch_thr=4, time_distance=0.5)
    selected_scenes.write_gifs(clip.resize(width=450), out_directory)


def get_output_directory(basedir, video):
    base_filename = os.path.splitext(os.path.basename(video))[0]
    outdir = os.path.join(basedir, base_filename)
    try:
        os.mkdir(outdir)
    except OSError:
        pass
    return outdir


if __name__ == '__main__':
    args = parse_arguments()
    for video in args.video:
        print("~ Processing: {}".format(os.path.basename(video)))
        process_vid(video, get_output_directory(args.outdir[0], video))
