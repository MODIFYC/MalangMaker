import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

// 명령어별 응답시간 추적
const writeTrend = new Trend('cmd_write');  // DB 쓰기 발생
const readTrend = new Trend('cmd_read');    // 읽기 전용

export const options = {
    stages: [
        // 1. 평상시 잠잠 (5분)
        { duration: '5m', target: 2 },

        // 2. 갑자기 폭증 (10초만에 50명!)
        { duration: '10s', target: 50 },
        { duration: '1m', target: 50 },   // 50명 유지

        // 3. 다시 잠잠 (15분 대기 → Lambda 컨테이너 내려감)
        { duration: '1m', target: 0 },    // 쿨다운
        { duration: '15m', target: 0 },   // Lambda 대기

        // 4. 콜드 스타트 후 다시 폭증 + 오래 버팀
        { duration: '10s', target: 50 },
        { duration: '10m', target: 50 },  // 10분 버티기
        { duration: '30s', target: 0 },   // 쿨다운
    ],
    thresholds: {
        http_req_duration: ['p(95)<3000'],
        http_req_failed: ['rate<0.05'],
    },
};

const URL = __ENV.MALANG_URL;
if (!URL) throw new Error('MALANG_URL 환경변수를 설정해주세요');

// 읽기 명령어
const readUtterances = ['/상태', '/도움', '/랭킹'];

// 쓰기 명령어 (DynamoDB 쓰기 발생)
const writeUtterances = ['/밥', '/쓰다듬기'];

function makePayload(utterance, userId) {
    return JSON.stringify({
        userRequest: {
            user: {
                id: userId,
                properties: { nickname: '테스터' }
            },
            utterance: utterance,
            chatRoom: { id: `test_room_${Math.floor(Math.random() * 5)}` }
        }
    });
}

export default function () {
    const userId = `test_user_${Math.floor(Math.random() * 30)}`;
    const params = { headers: { 'Content-Type': 'application/json' } };

    // 70% 읽기 / 30% 쓰기 (실제 사용 패턴 비슷하게)
    if (Math.random() < 0.7) {
        const utterance = readUtterances[Math.floor(Math.random() * readUtterances.length)];
        const res = http.post(URL, makePayload(utterance, userId), params);
        readTrend.add(res.timings.duration);
        check(res, {
            '[읽기] 응답 200': (r) => r.status === 200,
            '[읽기] 3초 이내': (r) => r.timings.duration < 3000,
        });
    } else {
        const utterance = writeUtterances[Math.floor(Math.random() * writeUtterances.length)];
        const res = http.post(URL, makePayload(utterance, userId), params);
        writeTrend.add(res.timings.duration);
        check(res, {
            '[쓰기] 응답 200': (r) => r.status === 200,
            '[쓰기] 3초 이내': (r) => r.timings.duration < 3000,
        });
    }

    sleep(1);
}