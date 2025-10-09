import argparse
import json
from korean_similarity_evaluator import KoreanSimilarityEvaluator

def main():
    """
    Command-line tool to calculate the similarity between two Korean sentences.
    """
    parser = argparse.ArgumentParser(
        description="Calculate similarity scores between two Korean sentences."
    )
    parser.add_argument("sentence1", type=str, help="The first sentence to compare.")
    parser.add_argument("sentence2", type=str, help="The second sentence to compare.")
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        help="The device to run BERTScore on (e.g., 'cpu', 'cuda').",
    )
    args = parser.parse_args()

    # Initialize the evaluator
    evaluator = KoreanSimilarityEvaluator(device=args.device)

    # Get the scores for the sentence pair
    scores = evaluator.evaluate_pair(args.sentence1, args.sentence2)

    # Print the results as a JSON object
    print(json.dumps(scores, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
