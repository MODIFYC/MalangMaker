import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

const strokeTrend = new Trend('cmd_stroke');
const cleanTrend = new Trend('cmd_clean');

export const options = {
    stages: [
        { duration: '10s', target: 10 },  // 10명으로 증가
        { duration: '30s', target: 10 },  // 30초 유지
        { duration: '10s', target: 0 },   // 종료
    ],
    thresholds: {
        http_req_duration: ['p(95)<3000'],
        http_req_failed: ['rate<0.05'],
    },
};

const URL = __ENV.MALANG_URL;
if (!URL) throw new Error('MALANG_URL 환경변수를 설정해주세요');

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
    const params = { headers: { 'Content-Type': 'application/json' } };

    // 유저 30명 중 랜덤 (각자 오늘치 1회)
    const userId = `test_user_${Math.floor(Math.random() * 30)}`;

    // 50% 쓰다듬기 / 50% 똥치우기
    if (Math.random() < 0.5) {
        const res = http.post(URL, makePayload('/쓰담', userId), params);
        strokeTrend.add(res.timings.duration);
        check(res, {
            '[쓰다듬기] 응답 200': (r) => r.status === 200,
            '[쓰다듬기] 3초 이내': (r) => r.timings.duration < 3000,
        });
    } else {
        const res = http.post(URL, makePayload('/똥', userId), params);
        cleanTrend.add(res.timings.duration);
        check(res, {
            '[똥치우기] 응답 200': (r) => r.status === 200,
            '[똥치우기] 3초 이내': (r) => r.timings.duration < 3000,
        });
    }

    sleep(1);
}