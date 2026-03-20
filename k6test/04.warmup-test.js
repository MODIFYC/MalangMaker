import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

const strokeTrend = new Trend('cmd_stroke');
const cleanTrend = new Trend('cmd_clean');

export const options = {
    stages: [
        { duration: '10s', target: 10 }, // 바로 요청
        { duration: '30s', target: 10 },
        { duration: '10s', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<3000'], // 웜업 됐으면 콜드스타트 없으니 3초
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
    const userId = `test_user_${Math.floor(Math.random() * 30)}`;

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
//   █ THRESHOLDS

//     http_req_duration
//     ✓ 'p(95)<3000' p(95)=78.63ms

//     http_req_failed
//     ✓ 'rate<0.05' rate=0.00%


//   █ TOTAL RESULTS

//     checks_total.......: 780     15.289753/s
//     checks_succeeded...: 100.00% 780 out of 780
//     checks_failed......: 0.00%   0 out of 780

//     ✓ [똥치우기] 응답 200
//     ✓ [똥치우기] 3초 이내
//     ✓ [쓰다듬기] 응답 200
//     ✓ [쓰다듬기] 3초 이내

//     CUSTOM
//     cmd_clean......................: avg=62.204939 min=43.4389 med=55.07975 max=284.0722 p(90)=76.55745 p(95)=82.202275
//     cmd_stroke.....................: avg=50.120531 min=35.6939 med=47.83275 max=237.3078 p(90)=59.86703 p(95)=64.334585

//     HTTP
//     http_req_duration..............: avg=56.19ms   min=35.69ms med=51.18ms  max=284.07ms p(90)=66.79ms  p(95)=78.63ms
//       { expected_response:true }...: avg=56.19ms   min=35.69ms med=51.18ms  max=284.07ms p(90)=66.79ms  p(95)=78.63ms
//     http_req_failed................: 0.00%  0 out of 390
//     http_reqs......................: 390    7.644877/s

//     EXECUTION
//     iteration_duration.............: avg=1.05s     min=1.03s   med=1.05s    max=1.28s    p(90)=1.06s    p(95)=1.08s
//     iterations.....................: 390    7.644877/s
//     vus............................: 1      min=1        max=10
//     vus_max........................: 10     min=10       max=10

//     NETWORK
//     data_received..................: 599 kB 12 kB/s
//     data_sent......................: 101 kB 2.0 kB/s



                                                                                                                                                              
// running (0m51.0s), 00/10 VUs, 390 complete and 0 interrupted iterations                                                                                       
// default ✓ [======================================] 00/10 VUs  50s       