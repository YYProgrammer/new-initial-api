# Initial API 文档

## 概述

Initial API用于返回用户输入query后的页面数据，在若干已支持的卡片中挑选一个最适合的卡片返回

## API 端点

**方法**: `POST`  
**响应类型**: 非Stream

## 请求参数

### 必需参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `query` | String | 用户输入的query |

### 可选参数
| `screen_content` | String | 前一屏幕的原始json数据信息 |



## 响应格式

### 通用示例
{
    "query": "xxxxxx",
    "card_list": [
        {
            "card_name": "InfoCard",
            "card_id": "card-23f90df4-82b1-xxxxxx",
            "data": {}
        }
    ]
}

### 响应参数含义

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `query` | String | 用户原query |
| `card_list` | List | 卡片列表 |
| `card_list[].card_name` | String | 卡片名称，用于区分显示什么卡片 |
| `card_list[].card_id` | String | 卡片id |
| `card_list[].data` | Object | 卡片所需数据，每个卡片data字段不相同 |


### 支持的卡片类型及选择逻辑

#### 概述
- 根据用户输入query和前一屏幕信息，分析用户意图，选择最适合的卡片
- 每个卡片会根据提供的必须参数，在卡片内部调用相关api或工具进行内容生成

#### 已有的具体卡片
- InfoCard：生成相关解释内容
- FlightsCard：搜索机票
- ShoppingCard：搜索amazon等平台的商品
- YelpCard：搜索餐馆
- Videos：搜索视频
- Images：搜索图片
- Translation：翻译
- Conversion：单位转换
- ChatCard：和AI聊天对话
- Comparison：对比两个商品
- PlanningCard：根据一个用户目标生成规划





## 不同组件(卡片)返回数据示例及解释

### 概述

在card_list里返回的元素，会有多种卡片类型，每种卡片的基础数据结构一致，data参数往往不同，下面详细罗列所有情况


### InfoCard

#### 示例

{
    "card_name": "InfoCard",
    "card_id": "xxxxxx",
    "data": {
        "query": "xxxx"
    }
}

#### InfoCard data 参数解释

| 参数名 | 类型 | 是否可空 | | 字段含义 | 生成逻辑 |
|--------|------|------|------|------|
| `query` | String | 不可空 | 调用ask brain api的query | 通过用户query和screen_content总结出的 | 




### FlightsCard

#### 示例

{
    "card_name": "FlightsCard",
    "card_id": "xxxxxx",
    "data": {
        "departure_location": "SFO",
        "arrival_location": "LAX",
        "trip_start_date": "2025-07-28 08:00:00",
        "trip_end_date": null,
        "adults": 1,
        "children": 0,
        "infants": 0,
        "flight_class": "ECONOMY",
        "suggestions": [
            {
                "departure_location": "SFO",
                "arrival_location": "LAX",
                "trip_start_date": "2025-07-28 08:00:00",
                "trip_end_date": null,
                "adults": 1,
                "children": 0,
                "infants": 0,
                "flight_class": "ECONOMY",
                "reason": "Los Angeles is a popular travel destination with diverse attractions."
            }
        ]
    }
}


#### FlightsCard data 参数解释

| 参数名 | 类型 | 是否可空 | | 字段含义 | 生成逻辑 |
|--------|------|------|------|------|
| `departure_location` | String | 不可空 | 出发地机场 | 通过用户query和screen_content生成，无法提取时测返回"" |
| `arrival_location` | String | 不可空 | 目的地机场 | 通过用户query/screen_content/header中的用户location生成，可默认SFO |
| `trip_start_date` | String | 不可空 | 出发时间 | 通过用户query/screen_content生成，可默认当前时间的第二天 |
| `trip_end_date` | String | 可空 | 返程时间，null时表示单程 | 通过用户query/screen_content生成 |
| `adults` | int | 不可空 | 成人人数 | 通过用户query/screen_content生成，可默认1 |
| `children` | int | 不可空 | 小孩人数 | 通过用户query/screen_content生成，可默认0 |
| `infants` | int | 不可空 | 婴儿人数 | 通过用户query/screen_content生成，可默认0 |
| `flight_class` | String | 不可空 | 航班座位类型 | 通过用户query/screen_content生成，必须是"ECONOMY"/"FIRST_CLASS"/”BUSINESS“中的一个，可默认ECONOMY |
| `suggestions` | List | 可空 | 航程建议 | 不可空的参数提取不到且无法提供默认值时，生成5条建议 |
| `suggestions[0].reason` | String | 不可空 | 航程建议原因 | 提供该项建议的原因 |







### ShoppingCard

#### 示例

{
    "card_name": "ShoppingSearchResults",
    "card_id": "xxxxxx",
    "data": {
        "search_query": "TV",
        "platforms": "Amazon",
        "gender": "all_gender",
        "brands": "Nike"
    }
}


#### ShoppingCard data 参数解释

| 参数名 | 类型 | 是否可空 | | 字段含义 | 生成逻辑 |
|--------|------|------|------|------|
| `search_query` | String | 不可空 | 商品搜索关键字 | 通过用户query和screen_content生成，无法提取时默认"Natural Phone" |
| `platforms` | String | 不可空 | 搜索平台 | 通过用户query和screen_content生成，必须是amazon/amazon_japan/yahoo_japan/rakuten/target/xlab平台具体商家中的一个或多个，如果是多个则用逗号分隔，可默认”Amazon“ |
| `gender` | String | 可空 | xlab搜索时传入的性别 | 通过用户query和screen_content生成，可默认all_gender |
| `brands` | String | 可空 | xlab搜索时传入的品牌 | 通过用户query和screen_content生成 |





### YelpCard

#### 示例

{
    "card_name": "YelpCard",
    "card_id": "xxxxxx",
    "data": {
        "keyword": "restaurant",
        "location": "Los Angeles",
        "categories": [
            "restaurants",
            "food",
            "pub",
            "pubs"
        ]
    }
}

#### YelpCard data 参数解释

| 参数名 | 类型 | 是否可空 | | 字段含义 | 生成逻辑 |
|--------|------|------|------|------|
| `keyword` | String | 不可空 | 搜索关键字 | 通过用户query和screen_content生成，可默认"restaurant" |
| `location` | String | 不可空 | 搜索地址 | 通过用户query和screen_content生成，可默认”San Francisco“ |
| `categories` | List | 不可空 | 搜索时搜索类型 | 直接默认返回["restaurants","food","pub","pubs"] |





### Videos

#### 示例

{
    "card_name": "Videos",
    "card_id": "xxxxxx",
    "data": {
        "topic": "NBA"
    }
}


#### Videos data 参数解释

| 参数名 | 类型 | 是否可空 | | 字段含义 | 生成逻辑 |
|--------|------|------|------|------|
| `topic` | String | 不可空 | 搜索关键字 | 通过用户query和screen_content生成，可默认"Popular" |






### Images

#### 示例

{
    "card_name": "Images",
    "card_id": "xxxxxx",
    "data": {
        "topic": "cat"
    }
}

#### Images data 参数解释

| 参数名 | 类型 | 是否可空 | | 字段含义 | 生成逻辑 |
|--------|------|------|------|------|
| `topic` | String | 不可空 | 搜索关键字 | 通过用户query和screen_content生成，可默认"Popular" |







### Translation

#### 示例

{
    "card_name": "Translation",
    "card_id": "xxxxxx",
    "data": {
        "input_text": "hello",
        "input_language": "English",
        "output_language": "Chinese",
        "output_text": "你好"
    }
}



#### Translation data 参数解释

| 参数名 | 类型 | 是否可空 | | 字段含义 | 生成逻辑 |
|--------|------|------|------|------|
| `input_text` | String | 不可空 | 需要翻译的文字 | 通过用户query和screen_content生成 |
| `input_language` | String | 不可空 | 需要翻译的文字 | 自动识别需要翻译的文字的语言 |
| `output_language` | String | 不可空 | 翻译目标语言 | 通过用户query和screen_content生成，可默认"English" |
| `output_text` | String | 可空 | 翻译结果 | 通过input_text+output_language生成，也可以不默认翻译由前端调用api执行翻译 |





### Conversion

#### 示例

{
    "card_name": "Conversion",
    "card_id": "xxxxxx",
    "data": {
        "input_value": "10",
        "input_unit": "RMB",
        "output_unit": "USD"
    }
}

#### Conversion data 参数解释

| 参数名 | 类型 | 是否可空 | | 字段含义 | 生成逻辑 |
|--------|------|------|------|------|
| `input_value` | String | 不可空 | 转换的内容 | 通过用户query和screen_content生成 |
| `input_unit` | String | 不可空 | 转换前的单位 | 通过用户query和screen_content生成 |
| `output_unit` | String | 不可空 | 转换后的单位 | 通过用户query和screen_content生成 |






### ChatCard

#### 示例

{
    "card_name": "Conversion",
    "card_id": "xxxxxx",
    "data": {
        "query": "let us chat"
    }
}

#### ChatCard data 参数解释

| 参数名 | 类型 | 是否可空 | | 字段含义 | 生成逻辑 |
|--------|------|------|------|------|
| `query` | String | 不可空 | 用户聊天默认发出的第一句话 | 通过用户query和screen_content生成 |







### Comparison

#### 示例

{
    "card_name": "Comparison",
    "card_id": "xxxxxx",
    "data": {
        "item_1": "iPhone 14"
        "item_2": "iPhone 15"
    }
}

#### Comparison data 参数解释

| 参数名 | 类型 | 是否可空 | | 字段含义 | 生成逻辑 |
|--------|------|------|------|------|
| `item_1` | String | 不可空 | 对比两项商品中的商品1 | 通过用户query和screen_content生成 |
| `item_2` | String | 不可空 | 对比两项商品中的商品2 | 通过用户query和screen_content生成 |




### PlanningCard

#### 示例

{
    "card_name": "PlanningCard",
    "card_id": "xxxxxx",
    "data": {
        "query": "plan a trip",
        "screen_content": ""
    }
}

#### PlanningCard data 参数解释

| 参数名 | 类型 | 是否可空 | | 字段含义 | 生成逻辑 |
|--------|------|------|------|------|
| `query` | String | 不可空 | 用户输入的内容 | 直接是用户原query |
| `screen_content` | String | 可空 | 屏幕信息 | 传入initial api时的原屏幕信息 |
