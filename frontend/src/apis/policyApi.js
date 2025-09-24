
// 백엔드 API 서버의 기본 주소
const API_BASE_URL = 'http://localhost:5001/api';

/**
 * 현재 적용된 모든 정책(온프레미스, 클라우드)을 가져옵니다.
 * @returns {Promise<Object>} API 응답 데이터
 */
export const getCurrentPolicies = async () => {
  const response = await fetch(`${API_BASE_URL}/policy/current`);
  if (!response.ok) {
    throw new Error('서버로부터 정책을 불러오는 데 실패했습니다.');
  }
  return response.json();
};

/**
 * 새로운 YAML 정책 파일을 서버에 전송하여 적용합니다.
 * @param {FormData} formData - policy_file을 포함하는 FormData 객체
 * @returns {Promise<Object>} API 응답 데이터
 */
export const applyNewPolicy = async (formData) => {
  const response = await fetch(`${API_BASE_URL}/policy/apply`, {
    method: 'POST',
    body: formData,
  });
  // 응답이 JSON이 아닐 수도 있으므로, 먼저 텍스트로 읽어본 후 파싱 시도
  const resultText = await response.text();
  try {
    return JSON.parse(resultText);
  } catch (e) {
    // JSON 파싱 실패 시, 원본 텍스트를 에러 메시지로 반환
    throw new Error(`서버 응답 처리 오류: ${resultText}`);
  }
};