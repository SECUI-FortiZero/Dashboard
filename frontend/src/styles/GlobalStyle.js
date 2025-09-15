import { createGlobalStyle } from 'styled-components';

const GlobalStyle = createGlobalStyle`
  /* 피그마 디자인에 사용된 폰트를 import 합니다 */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  body {
    margin: 0;
    font-family: 'Inter', sans-serif;
    background: linear-gradient(169deg, #0F123B 0%, #090D2E 59%, #020515 100%);
    color: white;
  }

  /* 다른 전역 스타일이 필요하면 여기에 추가합니다 */
  * {
    box-sizing: border-box;
  }
`;

export default GlobalStyle;