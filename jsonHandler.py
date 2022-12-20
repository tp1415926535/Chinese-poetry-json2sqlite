import json
import databaseManager
totalDics=[]

#将数据转储到database（json路径，表名，json字段和列映射关系，忽略的列表分隔）
def jsonSaveToDb(filePath,tablename,mapping,ignoreList):
	datas={}
	f = open(filePath,"r",encoding='utf-8')
	datas = json.load(f)
	f.close()

	global totalDics
	totalDics.clear()
	propertyName = mapping.values()
	for name in propertyName:
		ignoreList.append(name)
	JsonToOneLevel(datas,{},ignoreList)
	toDbDatas = totalDics

	nameIdDics={}#需要查其他表的字段，其他表的键值对
	for key in mapping:
		value = mapping[key]
		if value==None:#忽略id
			continue
		if isinstance(value, dict): #获取其他表的键值对
			fromtable = value["table"]
			queryColumn = value["queryColumn"]
			queryTarget = value["queryTarget"]
			nameIdDics[key]= databaseManager.getNameIdDic(fromtable,queryColumn,queryTarget)

	for item in toDbDatas:
		keys = list(item.keys()).copy()
		for key in keys: #移除不需要的数据
			if (key not in mapping.values()) | (key=="id"):
				del item[key]
		for key in mapping:
			if (key=="id") | (mapping[key]==None):#忽略id
				continue
			if key in nameIdDics:#从其他表读取目标列对应的值
				currentColumn = mapping[key]["currentColumn"]
				if (currentColumn in item) & (item[currentColumn] in nameIdDics[key]):
					item[key] = nameIdDics[key][item[currentColumn]]
				else:
					item[key] = -1
			else:
				item[key] = item.pop(mapping[key], None)#替换为新名
				if isinstance(item[key], list):
					item[key]=str(item[key])
	databaseManager.fillInToData(tablename,mapping.keys(),toDbDatas)#写入数据库


#将json树形结构压成单行数据（json字典，缓存键值对，忽略拆分的列表属性名）
def JsonToOneLevel(jsondata,tempDic,ignoreList):
	global totalDics

	tempDicList=[]
	tempDicCombine=tempDic.copy()

	childPropertyCount=0
	for key in jsondata:
		value = key
		if isinstance(jsondata, dict):
			value = jsondata[key]

		if isinstance(value, dict):
			childPropertyCount = childPropertyCount+1
		elif isinstance(value, list) & (key not in ignoreList):
			childPropertyCount = childPropertyCount+1
		else:
			tempDicCombine[key] = value

	for i in range(0,childPropertyCount):
		tempDicList.append(tempDicCombine.copy())

	index = 0
	for key in jsondata:
		value = key
		if isinstance(jsondata, dict):
			value = jsondata[key]

		if isinstance(value, dict):
			JsonToOneLevel(value,tempDicList[index],ignoreList)
			index = index + 1
		elif isinstance(value, list) &  (key not in ignoreList):
			JsonToOneLevel(value,tempDicList[index],ignoreList)
			index = index + 1

	if childPropertyCount<=0:
		totalDics.append(tempDicCombine)
