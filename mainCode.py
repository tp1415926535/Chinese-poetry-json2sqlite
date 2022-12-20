import json
import os
import fnmatch
import databaseManager
import jsonHandler
from datetime import datetime

configFile="config.json"
config={}

print("古诗词json转数据库sqlite\r\n开发：纵码过河山\r\n项目：https://github.com/tp1415926535/Chinese-poetry-json2sqlite")

def init():
	global configFile,config
	if os.path.exists(configFile):
		f = open(configFile,"r",encoding='utf-8')
		config = json.load(f)
		f.close()
	else:
		print("不存在配置文件，无法生成数据库！")
		input("按下回车键退出")
		sys.exit() 

	if ("dataSourceFolder" not in config)|("dbPath" not in config):
		print("未配置输入或输出路径！")
		input("按下回车键退出")
		sys.exit() 

	dataSourceFolder=os.path.realpath(config["dataSourceFolder"])
	if not os.path.exists(dataSourceFolder):
		print("未找到源数据文件夹。 请修改配置文件的 dataSourceFolder 值为 chinese-poetry 项目解压的文件夹路径！")
		input("按下回车键退出")
		sys.exit()

	databaseFile=os.path.realpath(config["dbPath"])
	if os.path.isfile(databaseFile):
		print("数据库文件已存在，写入可能会造成数据重复！有以下操作可以选择：\r\n1.自动删除已有数据库重建\r\n2.忽略警告继续添加\r\n3.退出程序修改配置路径")
		while True:
			result = input("请输入所选编号? ")
			if result=="1":
				os.remove(databaseFile)
				break
			elif result=="2":
				break
			elif result=="3":
				sys.exit()

	if ("tables" not in config)| (len(config["tables"])<=0):
		print("无数据需要建立，请添加配置文件 tables 的子项！")
		sys.exit()


def BuildDatabase():
	global config
	ignoreList=config["ignoreSplitListName"]
	dataSourceFolder=os.path.realpath(config["dataSourceFolder"])

	timeBegin=datetime.now()
	for table in config["tables"]:
		tablename= table["tableName"]
		targetFolder=os.path.join(dataSourceFolder, table["dataSource"]["folder"]).replace("/","\\")
		if os.path.isdir(targetFolder)==False:
			print(f"未找到 {tablename} 对应的来源文件夹 “{targetFolder}” ，跳过生成。")
			continue
		
		subFiles = [ f.name for f in os.scandir(targetFolder) if f.is_file() ]
		targetFiles = fnmatch.filter(subFiles, table["dataSource"]["fileNameFormat"])
		message="———————————————————————————————————————————————————\r\n"\
			f"正在创建表 {tablename} ，匹配到{len(targetFiles)}个json文件来源..."\
			"\r\n———————————————————————————————————————————————————"
		print(message)
		mapping = table["columns"]
		for file in targetFiles:
			print(f"正在写入json数据：{file}")
			try:
				jsonHandler.jsonSaveToDb(os.path.join(targetFolder,file),tablename,mapping,ignoreList.copy())
			except Exception as e:
				print(str(e))
	timeEnd = datetime.now()

	input(f"\r\n\r\n写入数据库完成，耗时{str(timeEnd-timeBegin)[:-7]}")
			
	


if __name__ == "__main__":
	try:
		init()
		databaseFile=os.path.realpath(config["dbPath"])
		databaseManager.connectDatabase(databaseFile)
		BuildDatabase()
	except Exception as e:
		print("【错误】"+str(e))
	input("按下回车键退出")