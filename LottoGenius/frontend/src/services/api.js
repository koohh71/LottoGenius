import axios from 'axios';

// 환경 변수 또는 현재 호스트 기반 동적 주소 설정
const BASE_URL = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

// Axios 인스턴스 생성
const api = axios.create({
    baseURL: BASE_URL,
    timeout: 10000, // 10초 타임아웃
});

export const lottoService = {
    // 최신 회차 조회
    getLatestRound: async () => {
        const response = await api.get('/api/latest-round');
        return response.data.latest_round;
    },

    // 통계 조회
    getStats: async (limit) => {
        const response = await api.get(`/api/stats?limit=${limit}`);
        return response.data;
    },

    // 번호 생성
    generateNumbers: async (params) => {
        // params: { history_limit, fixed_nums, excluded_nums, count }
        const response = await api.post('/api/generate', params);
        return response.data.recommendations;
    },

    // 회차 정보 수동 추가
    addRound: async (data) => {
        // data: { round_no, numbers, bonus }
        const response = await api.post('/api/add-round', data);
        return response.data;
    }
};
