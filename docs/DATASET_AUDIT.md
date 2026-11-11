# Dataset Label Noise Audit

## Summary
17 of 31 sampled buggy cases were really bug-introducing (noise rate 45.2%).

## Audit Parameters
- **Dataset file:** `datasets/requests.jsonl`
- **Source repository:** `C:\Users\Dhruv Parmar\Downloads\requests-fixture`
- **Sample size:** 50
- **Random seed:** 1
- **Evaluated cases:** 31 (17 verified bug-introducing, 14 label noise)
- **Skipped cases:** 19
- **Noise rate:** 45.2%

## Evaluated Cases
| # | Case ID | Commit SHA | Fix SHA | Verdict |
|---|---|---|---|---|
| 1 | `requests-fixture_400d27f982` | `400d27f982` | `cc23d1c644` | `y` |
| 2 | `requests-fixture_1988d9cf72` | `1988d9cf72` | `f0198e6dfc` | `n` |
| 3 | `requests-fixture_0caa243212` | `0caa243212` | `2d4a89f5dc` | `skip` |
| 4 | `requests-fixture_40402cd0dd` | `40402cd0dd` | `f8bec2f7ca` | `skip` |
| 5 | `requests-fixture_d24ee0e1dc` | `d24ee0e1dc` | `4246792b81` | `skip` |
| 6 | `requests-fixture_f9c0ddf46d` | `f9c0ddf46d` | `cfa627ae62` | `y` |
| 7 | `requests-fixture_36fd8da1c0` | `36fd8da1c0` | `3d0a1eb90d` | `n` |
| 8 | `requests-fixture_78f48aef8f` | `78f48aef8f` | `587385bfe0` | `y` |
| 9 | `requests-fixture_677bbe30d7` | `677bbe30d7` | `5fa4e74d61` | `y` |
| 10 | `requests-fixture_42ec8b08f2` | `42ec8b08f2` | `00c6ad58b7` | `y` |
| 11 | `requests-fixture_fb2931801e` | `fb2931801e` | `373a34a144` | `y` |
| 12 | `requests-fixture_2fddbe3606` | `2fddbe3606` | `74b7280049` | `y` |
| 13 | `requests-fixture_1451ba0c6d` | `1451ba0c6d` | `ed0242ae3a` | `y` |
| 14 | `requests-fixture_cfa627ae62` | `cfa627ae62` | `88c762e256` | `y` |
| 15 | `requests-fixture_cb2c800518` | `cb2c800518` | `4443b1a847` | `y` |
| 16 | `requests-fixture_204649521b` | `204649521b` | `b4bc76f8eb` | `y` |
| 17 | `requests-fixture_8aff6f5ed0` | `8aff6f5ed0` | `2255c34a65` | `y` |
| 18 | `requests-fixture_b34a496649` | `b34a496649` | `0713e09526` | `y` |
| 19 | `requests-fixture_6a415a02cf` | `6a415a02cf` | `9e681a4a9f` | `y` |
| 20 | `requests-fixture_6e76ab7188` | `6e76ab7188` | `6c41633cfd` | `y` |
| 21 | `requests-fixture_533c384b87` | `533c384b87` | `c45a4dfe6b` | `y` |
| 22 | `requests-fixture_33d448eb21` | `33d448eb21` | `3ed60078e2` | `y` |
| 23 | `requests-fixture_4193b95db0` | `4193b95db0` | `db575eeedc` | `n` |
| 24 | `requests-fixture_8112fcc7be` | `8112fcc7be` | `f8bec2f7ca` | `n` |
| 25 | `requests-fixture_05de270d7a` | `05de270d7a` | `0b42772663` | `n` |
| 26 | `requests-fixture_4d498db3ed` | `4d498db3ed` | `96efb5ec96` | `n` |
| 27 | `requests-fixture_a69cf7e71c` | `a69cf7e71c` | `177f4dd2a4` | `n` |
| 28 | `requests-fixture_c28da22e9c` | `c28da22e9c` | `6ff6f756c0` | `n` |
| 29 | `requests-fixture_55bf436f8f` | `55bf436f8f` | `8081d7b15c` | `n` |
| 30 | `requests-fixture_c2aeaa3959` | `c2aeaa3959` | `168109f13c` | `n` |
| 31 | `requests-fixture_18b29ea005` | `18b29ea005` | `4c8af1fff4` | `n` |
| 32 | `requests-fixture_596ca83f0c` | `596ca83f0c` | `79c4a017fe` | `n` |
| 33 | `requests-fixture_ca2ebc5b68` | `ca2ebc5b68` | `583859b820` | `n` |
| 34 | `requests-fixture_a17fdf6224` | `a17fdf6224` | `0af19a05ce` | `n` |
| 35 | `requests-fixture_012f0334ce` | `012f0334ce` | `2bbd7ba1c2` | `skip` |
| 36 | `requests-fixture_0792acc130` | `0792acc130` | `2c8721540a` | `skip` |
| 37 | `requests-fixture_b00d8bf474` | `b00d8bf474` | `571d2c2cd7` | `skip` |
| 38 | `requests-fixture_b1de7e7287` | `b1de7e7287` | `7197afa887` | `skip` |
| 39 | `requests-fixture_3440fca2e8` | `3440fca2e8` | `a4cd1a85d6` | `skip` |
| 40 | `requests-fixture_dfb4ef7be0` | `dfb4ef7be0` | `f5f3e696ab` | `skip` |
| 41 | `requests-fixture_afcc883d7f` | `afcc883d7f` | `6e76ab7188` | `skip` |
| 42 | `requests-fixture_9f55f503b1` | `9f55f503b1` | `42d0a2169e` | `skip` |
| 43 | `requests-fixture_83b4081e85` | `83b4081e85` | `ab8e43a196` | `skip` |
| 44 | `requests-fixture_1da62a65d9` | `1da62a65d9` | `fd31453aa2` | `skip` |
| 45 | `requests-fixture_0ab7a52f7c` | `0ab7a52f7c` | `26ed7c2e1d` | `skip` |
| 46 | `requests-fixture_0bb8be0e5b` | `0bb8be0e5b` | `537def4a4f` | `skip` |
| 47 | `requests-fixture_0a1e527aec` | `0a1e527aec` | `b4bc76f8eb` | `skip` |
| 48 | `requests-fixture_1532effb68` | `1532effb68` | `ed767cb703` | `skip` |
| 49 | `requests-fixture_a982b0d903` | `a982b0d903` | `a95bfd3032` | `skip` |
| 50 | `requests-fixture_d2590ee46c` | `d2590ee46c` | `e50dc12b0f` | `skip` |
