import sqlite3

connection=None
cur=None

def connectDatabase(file):
	global connection,cur
	connection = sqlite3.connect(file)
	connection.row_factory = sqlite3.Row
	cur = connection.cursor()

def createTable(tableName,columns):
	sql=f"create table if not exists {tableName} ("
	for column in columns:
		if column=="id":
			sql=sql+ "id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
		elif "_id" in column:
			sql=sql+ f'{column} INTEGER,'
		else:
			sql=sql+ f'{column} TEXT,'
	sql = sql[:-1] + ")"
	cur.execute(sql)
	connection.commit()

def fillInToData(tableName,columns,diclist):

	createTable(tableName,columns)
	if len(diclist)<=0:
		return

	insertcolumns=",".join(diclist[0].keys())
	tuplearray= [tuple(dic.values()) for dic in diclist]
	valuesTemplate="("
	for i in diclist[0].keys():
		valuesTemplate = valuesTemplate+"?,"
	valuesTemplate=valuesTemplate[:-1]+")"

	cur.executemany(f'INSERT INTO {tableName} ({insertcolumns}) VALUES {valuesTemplate}', tuplearray)
	connection.commit()


def getNameIdDic(tableName,columnName,idColumn):
	data={}
	sql=f'SELECT {idColumn},{columnName} FROM {tableName}'
	cur.execute(sql)
	results=cur.fetchall()
	for result in results:
		data[result[columnName]]=result[idColumn]
	return data
