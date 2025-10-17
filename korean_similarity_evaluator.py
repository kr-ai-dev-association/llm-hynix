import math
from typing import Dict, List, Tuple

from kiwipiepy import Kiwi
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer
from sacrebleu.metrics import BLEU
# BERTScore 관련 import는 제거했습니다.


class KoreanSimilarityEvaluator:
    """
    BLEU, ROUGE-L, METEOR만을 이용하여 두 한국어 문장의 유사도를 계산합니다.
    - 입력 문장은 Kiwi 형태소 분석을 통해 어근(표제어) 기반 토큰으로 정규화됩니다.
    - 정규화된 토큰은 공백으로 결합하여 BLEU/ROUGE/METEOR에 사용됩니다.
    - 최종 점수는 BLEU, ROUGE-L, METEOR 세 점수의 조화 평균(Harmonic Mean)으로 반환합니다.
    """

    def __init__(
        self,
        # 기존에 BERTScore용 파라미터가 있었지만, 현재는 사용되지 않으므로 기본값만 유지합니다.
        bert_model: str = "klue/bert-base",
        bert_model_path: str = None,
        device: str = "cpu",
    ) -> None:
        """
        Args:
            bert_model (str): 현재 사용되지 않음. 호환성을 위해 유지.
            bert_model_path (str, optional): 현재 사용되지 않음.
            device (str): 현재 사용되지 않음.
        """
        self.kiwi = Kiwi()
        self.bleu = BLEU(effective_order=True)
        # ROUGE 점수로 ROUGE-L F1을 사용합니다
        self.rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)
        # BERTScore 관련 속성은 더 이상 필요하지 않으므로 제거
        # self.bert_model = bert_model
        # self.bert_model_path = bert_model_path
        # self.device = device

    def _lemmatize_tokens(self, text: str) -> List[str]:
        tokens = []
        for t in self.kiwi.tokenize(text):
            lemma = None
            # 일부 버전은 lemma 속성을 제공합니다. 없으면 원형 대신 표면형(form)을 사용합니다
            try:
                lemma = getattr(t, "lemma", None)
            except Exception:
                lemma = None
            token_text = lemma if lemma else t.form
            # 공백과 유사한 토큰은 제거합니다
            if token_text and not token_text.isspace():
                tokens.append(token_text)
        return tokens

    def _texts_to_lexical_inputs(self, ref: str, hyp: str) -> Tuple[List[str], List[str], str, str]:
        ref_tokens = self._lemmatize_tokens(ref)
        hyp_tokens = self._lemmatize_tokens(hyp)
        ref_space = " ".join(ref_tokens)
        hyp_space = " ".join(hyp_tokens)
        return ref_tokens, hyp_tokens, ref_space, hyp_space

    @staticmethod
    def _harmonic_mean(values: List[float], eps: float = 1e-8) -> float:
        """
        주어진 값들의 조화 평균을 계산합니다.
        값이 0에 가깝거나 음수이면 0을 반환합니다.
        """
        valid = [max(v, 0.0) for v in values]
        if any(v <= eps for v in valid):
            return 0.0
        denom = sum(1.0 / (v + eps) for v in valid)
        return len(valid) / denom if denom > 0 else 0.0

    @staticmethod
    def _rouge_l_f1_by_tokens(ref_tokens: List[str], hyp_tokens: List[str]) -> float:
        # 토큰 시퀀스 기반 LCS를 이용한 ROUGE-L F1 계산
        n = len(ref_tokens)
        m = len(hyp_tokens)
        if n == 0 or m == 0:
            return 0.0
        # LCS DP
        dp = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if ref_tokens[i - 1] == hyp_tokens[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        lcs = dp[n][m]
        prec = lcs / m
        rec = lcs / n
        if prec + rec == 0:
            return 0.0
        return 2 * prec * rec / (prec + rec)

    def evaluate_pair(self, ref: str, hyp: str) -> Dict[str, float]:
        """
        두 문장에 대해 BLEU, ROUGE-L, METEOR 점수를 계산하고
        이 세 점수의 조화 평균을 반환합니다.
        """
        ref_tokens, hyp_tokens, ref_space, hyp_space = self._texts_to_lexical_inputs(ref, hyp)

        # BLEU (문장 단위), [0,1] 범위로 스케일링 - sacrebleu는 문자열 입력을 기대
        try:
            bleu_score = self.bleu.sentence_score(hyp_space, [ref_space]).score / 100.0
        except Exception:
            bleu_score = 0.0

        # 토큰 기반 ROUGE-L F1 (커스텀 구현)으로 안정적 계산
        rouge_l = self._rouge_l_f1_by_tokens(ref_tokens, hyp_tokens)

        # METEOR (토큰 리스트 사용)
        try:
            meteor = meteor_score([ref_tokens], hyp_tokens)
        except Exception:
            meteor = 0.0

        # 조화 평균 (BLEU, ROUGE-L, METEOR)
        hmean = self._harmonic_mean([bleu_score, rouge_l, meteor])

        return {
            "bleu": float(bleu_score),
            "rouge_l": float(rouge_l),
            "meteor": float(meteor),
            "harmonic_mean": float(hmean),
        }