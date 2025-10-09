import math
from typing import Dict, List, Tuple

from kiwipiepy import Kiwi
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer
from sacrebleu.metrics import BLEU
from bert_score import score as bert_score


class KoreanSimilarityEvaluator:
    """
    BLEU, ROUGE-L, METEOR, BERTScore를 이용하여 두 한국어 문장의 유사도를 계산합니다.
    - 입력 문장은 Kiwi 형태소 분석을 통해 어근(표제어) 기반 토큰으로 정규화됩니다.
    - 정규화된 토큰은 공백으로 결합하여 BLEU/ROUGE/METEOR에 사용됩니다.
    - BERTScore는 공백 결합된 정규화 문장을 klue/bert-base로 평가합니다.
    """

    def __init__(self, bert_model: str = "klue/bert-base", device: str = "cpu") -> None:
        self.kiwi = Kiwi()
        self.bleu = BLEU(effective_order=True)
        # ROUGE 점수로 ROUGE-L F1을 사용합니다
        self.rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)
        self.bert_model = bert_model
        self.device = device

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

        # klue/bert-base를 사용한 BERTScore(F1); 정규화된 문장 사용
        try:
            # klue/bert-base는 bert-score의 기본 레이어 매핑에 없을 수 있으므로 명시적으로 레이어 지정
            P, R, F = bert_score(
                cands=[hyp_space],
                refs=[ref_space],
                lang="ko",
                model_type=self.bert_model,
                num_layers=12,
                device=self.device,
                verbose=False,
                rescale_with_baseline=False,
            )
            bert_f1 = float(F[0].item())
        except Exception:
            bert_f1 = 0.0

        hmean = self._harmonic_mean([bleu_score, rouge_l, meteor, bert_f1])

        return {
            "bleu": float(bleu_score),
            "rouge_l": float(rouge_l),
            "meteor": float(meteor),
            "bertscore_f1": float(bert_f1),
            "harmonic_mean": float(hmean),
        }


