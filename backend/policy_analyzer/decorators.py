def pipeline(fetcher, masker, analyzer):
    """
    공통 파이프라인 데코레이터
    """
    def wrapper(policy_type="cloud", range_type="daily"):
        # 1. 정책 가져오기
        policies = fetcher(policy_type, range_type)
        if not policies:
            return "❌ 분석할 정책 데이터가 없습니다."

        # 2. 마스킹 처리
        masked_policies = masker(policies)

        # 3. AI 분석
        return analyzer(masked_policies)
    return wrapper
