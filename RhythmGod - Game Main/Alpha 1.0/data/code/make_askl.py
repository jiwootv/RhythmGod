import json

# 원래 주어진 JSON 구조
data = {
    "version": 0.1,
    "note_speed": 600,
    "map_name": "askl4",
    "chabo": {}
}

# chabo 안의 내용을 200번 반복
counter = 1
for i in range(20):
    for key, value in {
        "100": [1],
        "200": [2],
        "300": [3],
        "400": [4],
    }.items():
        data["chabo"][str(counter*2)] = value
        counter += 1

# JSON 형식으로 변환
json_output = json.dumps(data, indent=4)

# 결과 출력
print(json_output)
