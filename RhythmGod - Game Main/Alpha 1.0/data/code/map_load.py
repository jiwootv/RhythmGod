import json

class Chabo_map_load:
	def __init__(self, mapname):
		print("성공적으로 로드")
		# self.file_name = open(mapname+"\\Map1.json", "r")
		self.file_path = mapname
		self.json_data = self.load()
		print(self.json_data)
	def load(self):
		"""a = json.load(self.file_name)
		print(a["chabo"])
		for i in a["chabo"]:
			print(i, a["chabo"][i])"""
		with open(self.file_path, "r") as file:
			a = json.load(file)
			print(a["chabo"])
			for i in a["chabo"]:
				print(i, a["chabo"])
		return a
if __name__ == "__main__":
	print("JSON LOAD")
	C = Chabo_map_load("..\\map\\animals")


# 해결함