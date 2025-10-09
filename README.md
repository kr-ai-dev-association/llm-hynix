# 한국어 문장 유사도 평가 도구

## 1. 프로젝트 개요

본 프로젝트는 두 개의 한국어 문장 간의 의미적 및 구문적 유사도를 측정하는 Python 기반 도구입니다. 네 가지 주요 평가 지표(BLEU, ROUGE-L, METEOR, BERTScore)를 사용하여 종합적인 유사도 점수를 계산하고, 이를 조화 평균내어 최종 점수를 제공합니다.

모든 한국어 입력은 `Kiwi` 형태소 분석기를 통해 어근과 어미를 분리하여 토큰화되며, `klue/bert-base` 모델을 BERTScore에 활용하여 한국어 문맥에 대한 깊은 이해를 바탕으로 점수를 계산합니다.

## 2. 주요 기능

- **다중 메트릭 평가**: BLEU, ROUGE-L, METEOR, BERTScore를 종합하여 다각적인 유사도 평가를 수행합니다.
- **한국어 형태소 분석**: `kiwipiepy`를 사용하여 문장을 어근/어미 단위로 분해하고 정규화하여 분석 정확도를 높입니다.
- **사전 학습 모델 활용**: `klue/bert-base` 모델을 BERTScore에 적용하여 문장의 의미적 유사도를 정밀하게 측정합니다.
- **조화 평균**: 개별 지표 점수를 결합하여 하나의 종합 점수를 도출함으로써 직관적인 비교를 가능하게 합니다.
- **모듈화된 설계**: `KoreanSimilarityEvaluator` 클래스를 통해 다른 Python 프로젝트에서도 쉽게 유사도 측정 기능을 통합할 수 있습니다.
- **다양한 실행 스크립트**: 단일 쌍 비교, 테스트케이스 파일 전체 비교, 전체 쌍(All-Pairs) 비교 및 결과 랭킹 등 다양한 활용 시나리오를 지원합니다.

## 3. 설치 방법

### 사전 요구사항

- Python 3.8 이상

### 설치 절차

1.  **저장소 복제** (이미 프로젝트가 있는 경우 생략)
    ```bash
    git clone <repository-url>
    cd llm-hynix
    ```

2.  **가상환경 생성 및 활성화**
    ```bash
    # 가상환경 생성
    python3 -m venv venv

    # 가상환경 활성화 (macOS/Linux)
    source venv/bin/activate

    # 가상환경 활성화 (Windows)
    .\venv\Scripts\activate
    ```

3.  **의존성 패키지 설치**
    프로젝트 루트에 있는 `requirements.txt` 파일을 사용하여 필요한 모든 패키지를 설치합니다.
    ```bash
    pip install -r requirements.txt
    ```

## 4. 사용 방법

본 프로젝트는 여러 사용 시나리오에 맞춰 다양한 실행 스크립트를 제공합니다. 모든 명령어는 가상환경이 활성화된 상태에서 실행해야 합니다.

### 4.1. 두 문장 직접 비교 (`simCalKr.py`)

두 개의 문장을 직접 입력받아 유사도 점수를 JSON 형식으로 출력합니다.

-   **사용법**:
    ```bash
    python simCalKr.py "첫 번째 문장" "두 번째 문장"
    ```

-   **예시**:
    ```bash
    python simCalKr.py "오늘 날씨 정말 좋네요" "오늘은 참 좋은 날씨입니다"
    ```

-   **출력 형식**:
    ```json
    {
        "bleu": 0.xxxx,
        "rouge_l": 0.xxxx,
        "meteor": 0.xxxx,
        "bertscore_f1": 0.xxxx,
        "harmonic_mean": 0.xxxx
    }
    ```

### 4.2. 테스트케이스 파일 일대일 비교 (`run_similarity.py`)

`testcase.md` 파일에 있는 각 행의 `입력문장 1`과 `입력문장 2`를 일대일로 비교하여 `testresult.md` 파일에 결과를 저장합니다.

-   **사용법**:
    ```bash
    python run_similarity.py --input testcase.md --output testresult.md
    ```
    (파일 경로 인자는 기본값으로 설정되어 있어 생략 가능합니다.)

### 4.3. 테스트케이스 파일 전체 쌍 비교 (`run_similarity_all_pairs.py`)

`testcase.md` 파일의 `입력문장 1` 열에 있는 모든 문장과 `입력문장 2` 열에 있는 모든 문장을 조합하여 10x10 매트릭스 형태의 유사도 점수표를 생성하고 `testresult.md`에 저장합니다.

-   **사용법**:
    ```bash
    python run_similarity_all_pairs.py --input testcase.md --output testresult.md
    ```

### 4.4. 전체 쌍 결과 순위 정렬 (`rank_results.py`)

`run_similarity_all_pairs.py` 실행 결과물인 `testresult.md`와 원본 `testcase.md`를 읽어, 100개의 모든 문장 쌍을 조화 평균 점수가 높은 순으로 정렬하여 `ranked_testresult.md` 파일에 저장합니다.

-   **사용법**:
    ```bash
    python rank_results.py --results_file testresult.md --testcase_file testcase.md --output_file ranked_testresult.md
    ```

## 5. 파일 구조 및 설명

-   `korean_similarity_evaluator.py`: 핵심 로직이 담긴 클래스 파일. 텍스트 토큰화 및 4가지 지표 계산을 수행합니다.
-   `simCalKr.py`: 두 문장을 직접 비교하는 CLI 스크립트.
-   `run_similarity.py`: `testcase.md`를 읽어 일대일 비교를 수행하는 스크립트.
-   `run_similarity_all_pairs.py`: `testcase.md`를 읽어 전체 쌍(N x M) 비교를 수행하는 스크립트.
-   `rank_results.py`: 전체 쌍 비교 결과를 점수 순으로 정렬하는 스크립트.
-   `requirements.txt`: 프로젝트 의존성 패키지 목록.
-   `testcase.md`: 평가에 사용될 예시 문장 쌍이 담긴 마크다운 파일.
-   `testresult.md`: 평가 결과가 저장되는 마크다운 파일.
-   `ranked_testresult.md`: 순위별로 정렬된 평가 결과가 저장되는 마크다운 파일.
