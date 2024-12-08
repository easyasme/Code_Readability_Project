import argparse

from src.gold_finder import gold_finder as gf
from src.clustering import clustering
from src.helper import masking, data_loading as dl
from src.helper.output import out


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Golden",
        description="Find gold particles and their density in electron microscopy images"
    )
    
    parser.add_argument(
        "name",
        type=str,
        help="The name of the dataset to analyze. This is the name of the folder in the 'analyzed synapses' directory,"
             "e.g., 'S1' or 'S7'"
    )
    
    parser.add_argument(
        "-m", "--mask",
        action="store_true",
        help="Whether to apply the mask to the image before finding gold particles. Default: False"
    )
    
    parser.add_argument(
        "-v", "--visual",
        action="store_true",
        help="Whether to display the image with the gold particles marked on it. Default: False"
    )
    
    parser.add_argument(
        "--dataloc",
        type=str,
        default=None,
        help="The location to store the data CSV file. If not specified, the data will not be saved."
    )
    
    parser.add_argument(
        "--figloc",
        type=str,
        default=None,
        help="The location to store the figure shown with the -m flag. If not specified, the figure will not be saved."
    )
    
    return parser.parse_args()


def main():
    args = get_args()
    
    bundles = dl.get_image_bundles("./data/analyzed synapses/")
    bundle_dict = {bundle.name: bundle for bundle in bundles}
    
    if args.name not in bundle_dict:
        print(f"Dataset '{args.name}' not found")
        return
    
    bundle = bundle_dict[args.name]
    
    img_luminosity = gf.GoldFinder.get_avg_luminosity(bundle.image)
    image = masking.apply_mask(bundle.image, bundle.mask) if args.mask else bundle.image
    
    gold_locations = gf.GoldFinder(image, img_luminosity=img_luminosity).find_gold()
    clusters = clustering.gold_cluster(gold_locations, image.size)
    
    output_data = out.create_output_df(clusters)
    
    if args.dataloc is not None:
        output_data.to_csv(args.dataloc, index=False)
    
    out.gen_visualization(image, clusters, args.visual, args.figloc)


if __name__ == "__main__":
    main()
