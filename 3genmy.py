
from grid import Grid
from grid_visual import GRID_VISUAL_SMALL
from match_finder import MatchFinder

if __name__ == '__main__':
    x = Grid({'B': 0, 'R': 15},
             shape_draft=GRID_VISUAL_SMALL,
             colorlist=['B', 'G', 'Y', 'R', 'Z', 'X'],
             color_weights=[1, 1, 1, 2, 1, 1])  #
    x.test_some()
    print(f"Start grid: \n{x.visualize_grid(x.grid)}")
    print(f"Start original colormap: \n{x.visualize_colormap(cm=x.orig_colormap)}")
    print(f"Start colormap: \n{x.visualize_colormap(x.colormap)}")
    print(x.main_iter())
    print(f"AP {x.all_paths}")
    print(f"WP {x.winning_paths}")
    print(f"Start grid: \n{x.visualize_grid(x.grid)}")
    print(f"Start colormap: \n{x.visualize_colormap(x.colormap)}")
    finder = MatchFinder(x.grid)
    print(finder.find_matches())
