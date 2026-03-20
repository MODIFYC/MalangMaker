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



// ===============결과===================
// █ THRESHOLDS

//     http_req_duration
//     ✓ 'p(95)<3000' p(95)=73.12ms

//     http_req_failed
//     ✓ 'rate<0.05' rate=0.00%


//   █ TOTAL RESULTS

//     checks_total.......: 780     15.299967/s
//     checks_succeeded...: 100.00% 780 out of 780
//     checks_failed......: 0.00%   0 out of 780

//     ✓ [쓰다듬기] 응답 200
//     ✓ [쓰다듬기] 3초 이내
//     ✓ [똥치우기] 응답 200
//     ✓ [똥치우기] 3초 이내

//     CUSTOM
//     cmd_clean......................: avg=56.396554 min=39.5937 med=54.6075 max=104.4721 p(90)=69.14822 p(95)=75.06587
//     cmd_stroke.....................: avg=50.772654 min=35.4894 med=47.8089 max=160.6439 p(90)=62.9786  p(95)=70.36297

//     HTTP
//     http_req_duration..............: avg=53.69ms   min=35.48ms med=51.76ms max=160.64ms p(90)=67.5ms   p(95)=73.12ms
//       { expected_response:true }...: avg=53.69ms   min=35.48ms med=51.76ms max=160.64ms p(90)=67.5ms   p(95)=73.12ms
//     http_req_failed................: 0.00%  0 out of 390
//     http_reqs......................: 390    7.649984/s

//     EXECUTION
//     iteration_duration.............: avg=1.05s     min=1.03s   med=1.05s   max=1.34s    p(90)=1.06s    p(95)=1.07s
//     iterations.....................: 390    7.649984/s
//     vus............................: 1      min=1        max=10
//     vus_max........................: 10     min=10       max=10

//     NETWORK
//     data_received..................: 597 kB 12 kB/s
//     data_sent......................: 101 kB 2.0 kB/s



                                                                                                                                                                 
// running (0m51.0s), 00/10 VUs, 390 complete and 0 interrupted iterations                                                                                          
// default ✓ [======================================] 00/10 VUs  50s             