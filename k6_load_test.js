
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.1/index.js";

import http from 'k6/http';
import { check } from 'k6';


export function handleSummary(data) {
    return {
      "results.html": htmlReport(data),
      stdout: textSummary(data, { indent: " ", enableColors: true }),
    };
  }
 
export const options = {
    vus: 10,
    duration: '5s',
    thresholds: {
        checks: ['rate==1.00'], // Ensure 100% of checks must pass
    },
};


export default function () {
    // Define request headers from original fetch API example
    let headers = {
        "Accept": "application/json, text/plain, */*",
        "gaid": "e3e92938-0b86-4ac5-9270-08e85ee30b0c",
        "AppVersion": "123",
        "Platform": "android",
        "SID": "1719303489596-28317",
        "TS": "undefined",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiZ21pUHJvZmlsZUlkIjoxOTcwNTUyOSwiZXhwIjoxNzI0NTA3MjExLCJmcmVlZmlyZVByb2ZpbGVJZCI6MTk3MDU1MzAsImlhdCI6MTcyMTkxNTIxMSwiaWQiOjExNzU4NzI5fQ.RBBs7_TDdeUz1bYVVria1P4fJ7d9XjY1_9tTVCfarhY"
    };

   
    let getLiveClubs = http.get("https://api.getstan.app/api/v5/get/live-clubs?limit=10&offset=0", { headers: headers });

   
    check(getLiveClubs, {
        'live-clubs? status is 200': r => r.status === 200,
        'live-clubs? body is not empty': (r) => r.body.length > 0,
     });
     if (getLiveClubs.status !== 200) {
        console.log('Response received: ' + getLiveClubs.body);
      }


    let getUpcominClubs = http.get("https://api.getstan.app/api/v5/get/upcoming-clubs?limit=10&offset=0", { headers: headers });
    check(getUpcominClubs, {
        "upcoming-clubs? status 200": (r) => r.status === 200,
        "upcoming-clubs? body is not empty": (r) => r.body.length > 0
    });
    
    if (getUpcominClubs.status !== 200) {
        console.log('Response received: ' + getUpcominClubs.body);
      }


    // let ur3 = 'https://api.getstan.app/api/v5/club/messages?clubId=AGPCIUE7';
    let clubMessages = http.get("https://api.getstan.app/api/v5/club/messages", { headers: headers });
    check(clubMessages, {
        "club/messages? status 200": (r) => r.status === 200,
        "club/messages? body  is not empty": (r) => r.body.length > 0
    });

    if (clubMessages.status !== 200) {
        console.log('Response received: ' + clubMessages.body);
      }


    let ClubPassBalance = http.get("https://api.getstan.app/api/v4/club-pass/balance", { headers: headers });
    check(ClubPassBalance, {
        "club-pass/balance status 200": (r) => r.status === 200,
        "club-pass/balance body  is not empty": (r) => r.body.length > 0
    });

    if (ClubPassBalance.status !== 200) {
        console.log('Response received: ' + ClubPassBalance.body);
      }

    let clubGiftFetch = http.get("https://api.getstan.app/api/v4/club-gift/fetch-inventory", { headers: headers });
    check(clubGiftFetch, {
        "club-gift/fetch-inventory status 200": (r) => r.status === 200,
        "club-gift/fetch-inventory body  is not empty": (r) => r.body.length > 0
    });

    if (clubGiftFetch.status !== 200) {
        console.log('Response received: ' + clubGiftFetch.body);
      }



    let agoraClubGifts = http.get("https://api.getstan.app/api/v1/agora/club-gifts", { headers: headers });
    check(agoraClubGifts, {
        "agora/club-gifts status 200": (r) => r.status === 200,
        "agora/club-gifts body  is not empty": (r) => r.body.length > 0
    });

    if (agoraClubGifts.status !== 200) {
        console.log('Response received: ' + agoraClubGifts.body);
      }



    let clubPassGetSku = http.get("https://api.getstan.app/api/v4/club-pass/getSKU", { headers: headers });
    check(clubPassGetSku, {
        "club-pass/getSKU status 200": (r) => r.status === 200,
        "club-pass/getSKU body  is not empty": (r) => r.body.length > 0
    });

    if (clubPassGetSku.status !== 200) {
        console.log('Response received: ' + clubPassGetSku.body);
      }



    let clubsRewards = http.get("https://api.getstan.app/api/v5/clubs/rewards", { headers: headers });
    check(clubsRewards, {
        "clubs/rewards status 200": (r) => r.status === 200,
        "clubs/rewards body  is not empty": (r) => r.body.length > 0
    });

    if (clubsRewards.status !== 200) {
        console.log('Response received: ' + clubsRewards.body);
      }


    let clubPastRewards = http.get("https://api.getstan.app/api/v5/clubs/rewards/past", { headers: headers });
    check(clubPastRewards, {
        "clubs/rewards/paststatus 200": (r) => r.status === 200,
        "clubs/rewards/past body  is not empty": (r) => r.body.length > 0
    });

    if (clubPastRewards.status !== 200) {
        console.log('Response received: ' + clubPastRewards.body);
      }


    let userClub = http.get("https://api.getstan.app/api/v5/user/club", { headers: headers });
    check(userClub, {
        "user/club status 200": (r) => r.status === 200,
        "user/club body  is not empty": (r) => r.body.length > 0
    });

    if (userClub.status !== 200) {
        console.log('Response received: ' + userClub.body);
      }

    let clubCategories = http.get("https://api.getstan.app/api/v5/club/categories", { headers: headers });
    check(clubCategories, {
        "club/categories status 200": (r) => r.status === 200,
        "club/categories body  is not empty": (r) => r.body.length > 0
    });

    if (clubCategories.status !== 200) {
        console.log('Response received: ' + clubCategories.body);
      }

    // console.log(`Response time for live-clubs endpoint: ${response.timings.duration} ms`);
}
