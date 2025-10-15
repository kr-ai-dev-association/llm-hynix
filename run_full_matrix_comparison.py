import re
from typing import List, Tuple

from korean_similarity_evaluator import KoreanSimilarityEvaluator


def parse_sentence_pairs(md_text: str) -> Tuple[List[str], List[str]]:
    """Parses a markdown table to extract all sentences from both columns."""
    sentences1: List[str] = []
    sentences2: List[str] = []
    lines = [ln.strip() for ln in md_text.splitlines()]
    
    # 마크다운 테이블에서 "| 번호 | 입력문장1 | 입력문장2 |" 형태의 행을 찾습니다
    for ln in lines:
        if ln.startswith("|") and ln.endswith("|"):
            cells = [c.strip() for c in ln.split("|")][1:-1]
            if len(cells) >= 3 and cells[0].isdigit():
                sent1 = cells[1]
                sent2 = cells[2]
                sentences1.append(sent1)
                sentences2.append(sent2)
    return sentences1, sentences2


def main():
    import argparse
    import pathlib
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="testcase.md")
    parser.add_argument("--output", default="full_matrix_comparison_result.md")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    text = input_path.read_text(encoding="utf-8")
    sentences1, sentences2 = parse_sentence_pairs(text)

    evaluator = KoreanSimilarityEvaluator(device=args.device)

    # Prepare markdown output
    content = [
        "# 한국어 문장 유사도 평가 결과 (전체 매트릭스 비교)",
        "",
        "## 테스트 환경",
        "- **평가 모델**: KoreanSimilarityEvaluator",
        "- **평가 방식**: 전체 매트릭스 비교",
        f"- **입력문장1 개수**: {len(sentences1)}개",
        f"- **입력문장2 개수**: {len(sentences2)}개",
        f"- **총 비교 쌍**: {len(sentences1) * len(sentences2)}개",
        "",
        "## 입력문장1 vs 입력문장2 매트릭스",
        ""
    ]

    # Create matrix table
    header = ["| 입력문장1 \\ 입력문장2 |"] + [f" {i+1} |" for i in range(len(sentences2))]
    align = ["| :--- |"] + [":---:|" for _ in range(len(sentences2))]
    
    content.extend(["".join(header), "".join(align)])

    # Calculate all similarities
    matrix = []
    for i, s1 in enumerate(sentences1):
        row = [f"| **{i+1}** |"]
        row_scores = []
        for j, s2 in enumerate(sentences2):
            result = evaluator.evaluate_pair(s1, s2)
            harmonic_mean = result["harmonic_mean"]
            row.append(f" {harmonic_mean:.4f} |")
            row_scores.append(harmonic_mean)
        matrix.append(row_scores)
        content.append("".join(row))

    content.extend([
        "",
        "## 입력문장별 상세 분석",
        ""
    ])

    # Detailed analysis for each sentence1
    for i, s1 in enumerate(sentences1):
        content.extend([
            f"### 입력문장1-{i+1} 분석",
            "",
            f"**문장**: {s1}",
            "",
            "**모든 입력문장2와의 유사도**:",
            ""
        ])
        
        # Get similarities with all sentences2
        similarities = []
        for j, s2 in enumerate(sentences2):
            result = evaluator.evaluate_pair(s1, s2)
            harmonic_mean = result["harmonic_mean"]
            similarities.append((j+1, harmonic_mean, s2))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        for rank, (j, score, s2) in enumerate(similarities, 1):
            content.extend([
                f"{rank}. **입력문장2-{j}**: {score:.4f}",
                f"   - 내용: {s2[:80]}...",
                ""
            ])
        
        content.append("---")
        content.append("")

    # Detailed analysis for each sentence2
    content.extend([
        "## 입력문장2별 상세 분석",
        ""
    ])

    for i, s2 in enumerate(sentences2):
        content.extend([
            f"### 입력문장2-{i+1} 분석",
            "",
            f"**문장**: {s2}",
            "",
            "**모든 입력문장1과의 유사도**:",
            ""
        ])
        
        # Get similarities with all sentences1
        similarities = []
        for j, s1 in enumerate(sentences1):
            result = evaluator.evaluate_pair(s1, s2)
            harmonic_mean = result["harmonic_mean"]
            similarities.append((j+1, harmonic_mean, s1))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        for rank, (j, score, s1) in enumerate(similarities, 1):
            content.extend([
                f"{rank}. **입력문장1-{j}**: {score:.4f}",
                f"   - 내용: {s1[:80]}...",
                ""
            ])
        
        content.append("---")
        content.append("")

    # Overall statistics
    all_scores = [score for row in matrix for score in row]
    content.extend([
        "## 전체 통계",
        "",
        f"- **평균 유사도**: {sum(all_scores) / len(all_scores):.4f}",
        f"- **최고 유사도**: {max(all_scores):.4f}",
        f"- **최저 유사도**: {min(all_scores):.4f}",
        f"- **표준편차**: {(sum((x - sum(all_scores)/len(all_scores))**2 for x in all_scores) / len(all_scores))**0.5:.4f}",
        "",
        "## 최고 유사도 쌍 (상위 10개)",
        ""
    ])
    
    # Find top 10 pairs
    all_pairs = []
    for i, s1 in enumerate(sentences1):
        for j, s2 in enumerate(sentences2):
            score = matrix[i][j]
            all_pairs.append((i+1, j+1, score, s1, s2))
    
    all_pairs.sort(key=lambda x: x[2], reverse=True)
    
    for rank, (i, j, score, s1, s2) in enumerate(all_pairs[:10], 1):
        content.extend([
            f"{rank}. **입력문장1-{i} vs 입력문장2-{j}**: {score:.4f}",
            f"   - 입력문장1: {s1[:60]}...",
            f"   - 입력문장2: {s2[:60]}...",
            ""
        ])

    output_path.write_text("\n".join(content), encoding="utf-8")
    print(f"Full matrix comparison results saved to {output_path}")


if __name__ == "__main__":
    main()
