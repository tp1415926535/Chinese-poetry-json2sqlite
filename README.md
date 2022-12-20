# Chinese-poetry-json2sqlite
将古诗词json转为sqlite本地数据库文件

**当前版本的作者id读取有点bug，正在修复中...**

# 前言
* 最近想用诗词库查询，但是最知名的库 [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) 是json数据，看了看其他转数据库的项目都是已经好几年前的了，有的json格式对不上，有的还需要其他开发环境，非常不人性化，所以写了这个可以兼容不同json来源的转sqlite本地数据库表的项目。   
* 为了适配各种json数据，本项目的霸道之处在于理论上可以匹配任何键值对形式的json，只需要调整配置文件即可（好像意外的实现了不得了的东西），所以不会编程也能改，也不会出现我遇到的json结构变化导致其他人的导出代码用不了还要研究源码的尴尬情况。
  
# 使用方法
* **方法1**：下载本项目的[Release](https://github.com/tp1415926535/Chinese-poetry-json2sqlite/releases/latest)的成品数据库文件。    
* **方法2**：下载本项目文件，和最新版的 chinese-poetry 项目文件，修改 config.json 配置文件。然后运行 mainCode.py 脚本，或者封装好的 mainCode.exe 即可。目前生成数据库只需要三分钟左右。

## 配置文件说明
文件 **“config.json”** ，需要跟python脚本或者exe放在同一个目录下。
它的内容大概是这样：
```json
{
    "dbPath": "Chinese-poetry.db",  //生成的数据库文件路径（支持相对路径和绝对路径）
    "dataSourceFolder": "../chinese-poetry-master", //项目 chinese-poetry 的下载解压后文件夹路径（支持相对路径和绝对路径）
    "ignoreSplitListName": [ //忽略分割列表的属性名，有些诗词json带着一些列表不需要分隔，进行排除。
        "tags",
        "paragraphs",
        "abstract",
        "preface"
    ],
    "tables": [ //将要写入数据库的表集合
        {
            "tableName": "ci_song_author",  //写入的表名
            "dataSource": {
                "folder": "ci", //该表的数据来源的文件夹（相对于 dataSourceFolder 的子目录）
                "fileNameFormat": "author.song.json"  //该表的数据来源的文件夹内文件名 (可以用*号模糊匹配多个json文件）
            },
            "columns": {  //表的结构，左边为列名，右边为json的字段名
                "id": null,  //id列，默认带上
                "name": "name",  //匹配到的json文件的 name 字段 写入表的 name 列中
                "short_description": "short_description",   //同理
                "description": "description"
            }
        },
        {
            "tableName": "ci_song",  //写入的表名
            "dataSource": {
                "folder": "ci",  //该表的数据来源的文件夹
                "fileNameFormat": "ci.song.*.json"  //该表的数据来源的文件夹内文件名，用 * 号代替任意内容，将获取到多个文件
            },
            "columns": {
                "id": null, // id列，默认带上
                "author_id": {  //author_id 无法从json文件中直接获取，这里通过其他表读取
                    "table": "ci_song_author", //读取的目标表
                    "currentColumn": "author", //查询依据的当前json字段
                    "queryColumn": "name",     //查询目标表的对应列
                    "queryTarget": "id"        //查询目标表返回值所在列
                },  //这段相当于 author_id 的值为 从表“ci_song_author” 中查询 "name" 列中 和json的“author” 字段值相同的数据，并返回该行数据的 id 值。
                "author": "author", //匹配到的json文件的 author 字段 写入表的 author 列中
                "rhythmic": "rhythmic",//同理
                "paragraphs": "paragraphs"
            }
        }
    ]
}
```
一般情况下，只需要修改["tables"]数组对应的表即可调整生成的结构和目标字段，或者如果新增了其他来源文件夹，可以再新增一条这样的配置数据：
```json
        {
            "tableName": "xxxxxx",
            "dataSource": {
                "folder": "xxxxxx",
                "fileNameFormat": "xxxxxxx.json"
            },
            "columns": { 
                "id": null,  
                "xxx": "xxx"
            }
        }
```


## 注意事项
  虽然这个代码兼容性已经很强了，但是还要注意json数据来源的格式。
  json数据源字段名应该放在值内，而不是放在键里，如：
```json
[
  { 
      "title":"标题1",
      "item":
      {
        "author": "xxxxx", 
        "rhythmic": "xxxxxx"
      }
  }, 
  { 
      "title":"标题2",
      "item": 
      {
        "author": "xxxxx", 
        "rhythmic": "xxxxxx"
      }
  },
]
```
   而不是直接作为键：
```json
{
    "标题1": 
    {
      "author": "xxxxx", 
      "rhythmic": "xxxxxx"
    }, 
    "标题2": 
    {
      "author": "xxxxx", 
      "rhythmic": "xxxxxx"
    }
}
```
  这是完全不同的格式，会导致出现错误的结果。所幸的是 chinese-poetry 的json格式是统一的，只要数据源是前者的格式即可正常运行。
