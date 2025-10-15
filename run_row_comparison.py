import re
from typing import List, Tuple

from korean_similarity_evaluator import KoreanSimilarityEvaluator


def parse_sentence_pairs(md_text: str) -> List[Tuple[str, str]]:
    """Parses a markdown table to extract pairs of sentences from each row."""
    pairs: List[Tuple[str, str]] = []
    lines = [ln.strip() for ln in md_text.splitlines()]
    
    # 마크다운 테이블에서 "| 번호 | 입력문장1 | 입력문장2 |" 형태의 행을 찾습니다
    for ln in lines:
        if ln.startswith("|") and ln.endswith("|"):
            cells = [c.strip() for c in ln.split("|")][1:-1]
            if len(cells) >= 3 and cells[0].isdigit():
                sent1 = cells[1]
                sent2 = cells[2]
                pairs.append((sent1, sent2))
    return pairs


def main():
    import argparse
    import pathlib
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="testcase.md")
    parser.add_argument("--output", default="row_comparison_result.md")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    text = input_path.read_text(encoding="utf-8")
    pairs = parse_sentence_pairs(text)

    evaluator = KoreanSimilarityEvaluator(device=args.device)

    # Prepare markdown output
    content = [
        "# 한국어 문장 유사도 평가 결과 (행별 비교)",
        "",
        "## 테스트 환경",
        "- **평가 모델**: KoreanSimilarityEvaluator",
        "- **평가 방식**: 각 행의 입력문장1과 입력문장2 비교",
        f"- **총 테스트 케이스**: {len(pairs)}개",
        "",
        "## 행별 유사도 분석",
        ""
    ]

    for i, (sent1, sent2) in enumerate(pairs, 1):
        result = evaluator.evaluate_pair(sent1, sent2)
        harmonic_mean = result["harmonic_mean"]
        
        content.extend([
            f"### 테스트 케이스 {i}",
            "",
            f"**유사도 점수**: {harmonic_mean:.4f}",
            "",
            "**입력문장 1**:",
            f"> {sent1}",
            "",
            "**입력문장 2**:",
            f"> {sent2}",
            "",
            "---",
            ""
        ])

    # Add summary
    content.extend([
        "## 전체 분석 요약",
        "",
        "### 유사도 점수 순위",
        ""
    ])
    
    # Calculate all scores and sort
    scores = []
    for i, (sent1, sent2) in enumerate(pairs, 1):
        result = evaluator.evaluate_pair(sent1, sent2)
        harmonic_mean = result["harmonic_mean"]
        scores.append((i, harmonic_mean, sent1, sent2))
    
    # Sort by score (descending)
    scores.sort(key=lambda x: x[1], reverse=True)
    
    for rank, (i, score, sent1, sent2) in enumerate(scores, 1):
        content.extend([
            f"{rank}. **테스트 케이스 {i}**: {score:.4f}",
            f"   - 입력문장1: {sent1[:50]}...",
            f"   - 입력문장2: {sent2[:50]}...",
            ""
        ])
    
    content.extend([
        "### 통계 정보",
        "",
        f"- **평균 유사도**: {sum(s[1] for s in scores) / len(scores):.4f}",
        f"- **최고 유사도**: {max(s[1] for s in scores):.4f} (테스트 케이스 {max(scores, key=lambda x: x[1])[0]})",
        f"- **최저 유사도**: {min(s[1] for s in scores):.4f} (테스트 케이스 {min(scores, key=lambda x: x[1])[0]})",
        ""
    ])

    output_path.write_text("\n".join(content), encoding="utf-8")
    print(f"Row comparison results saved to {output_path}")


if __name__ == "__main__":
    main()
