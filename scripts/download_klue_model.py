"""
klue/bert-base 모델을 로컬 디렉터리로 다운로드하는 유틸리티 스크립트

사용법:
    python scripts/download_klue_model.py --repo_id klue/bert-base --cache_dir ./models/klue-bert-base

옵션:
    --repo_id   : Hugging Face 레포지토리 ID (기본값: klue/bert-base)
    --cache_dir : 모델을 저장할 로컬 경로 (기본값: ./models/klue-bert-base)
    --revision  : 특정 커밋, 브랜치, 태그 (기본값: main)
    --token     : 비공개 레포지토리 접근이 필요할 경우 Hugging Face 토큰
"""

import argparse
import os
from pathlib import Path

from huggingface_hub import snapshot_download, HfApi

# ----------------------------------------------------------------------
# Hugging Face Hub 버전에 따라 예외 클래스가 위치가 다를 수 있습니다.
# 최신 버전에서는 RepositoryNotFoundError, RevisionNotFoundError 가
# huggingface_hub.utils._errors 모듈에 정의되어 있지만, 일부 버전에서는
# 직접 import 할 수 없습니다. 따라서 ImportError 발생 시 일반 Exception
# 로 대체하여 예외 처리를 유지합니다.
# ----------------------------------------------------------------------
try:
    # huggingface_hub 0.35.3 기준
    from huggingface_hub import RepositoryNotFoundError, RevisionNotFoundError
except ImportError:  # pragma: no cover
    RepositoryNotFoundError = Exception
    RevisionNotFoundError = Exception


def download_model(repo_id: str, cache_dir: Path, revision: str = "main", token: str = None):
    """
    Hugging Face Hub에서 지정된 레포지토리의 전체 스냅샷을 로컬 디렉터리로 다운로드합니다.
    이미 존재하는 경우에는 재다운로드를 건너뜁니다.

    Parameters
    ----------
    repo_id : str
        예: "klue/bert-base"
    cache_dir : Path
        모델을 저장할 디렉터리 (예: ./models/klue-bert-base)
    revision : str, optional
        커밋 SHA, 브랜치, 태그 등. 기본값은 "main".
    token : str, optional
        비공개 레포지토리 접근용 토큰.
    """
    # huggingface_hub 은 cache_dir 아래에 repo_id 폴더를 만든다.
    # 따라서 실제 파일이 들어갈 디렉터리는 `local_dir` 로 지정한다.
    try:
        print(f"🚀 {repo_id} 레포지토리를 {cache_dir} 로 다운로드 중...")
        snapshot_download(
            repo_id=repo_id,
            revision=revision,
            cache_dir=str(cache_dir.parent),   # huggingface_hub 은 cache_dir 아래에 repo_id 폴더를 만든다.
            local_dir=str(cache_dir),          # 최종 파일이 들어갈 디렉터리
            token=token,
            resume_download=True,
            force_download=False,
        )
        print(f"✅ 다운로드 완료! 모델 파일이 {cache_dir} 에 저장되었습니다.")
    except RepositoryNotFoundError:
        print(f"❌ 레포지토리 {repo_id} 를 찾을 수 없습니다.")
    except RevisionNotFoundError:
        print(f"❌ 지정한 revision({revision}) 이(가) 존재하지 않습니다.")
    except Exception as e:
        print(f"❌ 다운로드 중 오류 발생: {e}")


def main():
    parser = argparse.ArgumentParser(description="klue/bert-base 모델을 로컬에 다운로드합니다.")
    parser.add_argument(
        "--repo_id",
        type=str,
        default="klue/bert-base",
        help="Hugging Face 레포지토리 ID (예: klue/bert-base)",
    )
    parser.add_argument(
        "--cache_dir",
        type=str,
        default="./models/klue-bert-base",
        help="모델을 저장할 로컬 디렉터리 경로",
    )
    parser.add_argument(
        "--revision",
        type=str,
        default="main",
        help="레포지토리의 커밋/브랜치/태그 (기본: main)",
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="비공개 레포지토리 접근용 Hugging Face 토큰",
    )
    args = parser.parse_args()

    cache_path = Path(args.cache_dir).resolve()
    # 디렉터리가 없으면 생성합니다.
    cache_path.mkdir(parents=True, exist_ok=True)

    download_model(
        repo_id=args.repo_id,
        cache_dir=cache_path,
        revision=args.revision,
        token=args.token,
    )


if __name__ == "__main__":
    main()