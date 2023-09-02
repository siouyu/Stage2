from flask import *
import mysql.connector

app = Flask(__name__)

app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True

def connection():
    con = mysql.connector.connect(
        user = "root",
        password = "test", 
        host = "127.0.0.1",
        database = "website",
    )
    return con

# Pages
@app.route("/") # 已寫好的路由函式，勿更動！
def index():
	return render_template("index.html") 

@app.route("/attraction/<id>") # 已寫好的路由函式，勿更動！
def attraction(id):
	return render_template("attraction.html")

@app.route("/booking") # 已寫好的路由函式，勿更動！
def booking():
	return render_template("booking.html")

@app.route("/thankyou") # 已寫好的路由函式，勿更動！
def thankyou():
	return render_template("thankyou.html")


# 取得景點資料列表
@app.route("/api/attractions")
def get_attractions():	
	cursor = None
	try:
		con = connection()
		cursor = con.cursor(dictionary = True)
		page = int(request.args.get("page", 0))
		keyword = request.args.get("keyword", None)
		query = "SELECT * FROM Attraction"
		params = []

		if keyword:
			query += f" WHERE name LIKE %s OR mrt LIKE %s" 
			keyword = f"%{keyword}%"  # f 是 format、% 是前後模糊
			params = [keyword, keyword]

		per_page = 12
		offset = page * per_page
		query += " LIMIT %s OFFSET %s"
		params += [per_page, offset]

		cursor.execute(query, params)
		attractions = cursor.fetchall()

		for attraction in attractions:
			image_query = "SELECT image FROM Attraction_image WHERE attraction_id = %s"
			cursor.execute(image_query, [attraction['id']])
			images = cursor.fetchall()
			attraction["images"] = [img['image'] for img in images]

		cursor.close()
		con.close()

		has_more_data = len(attractions) == per_page
		response_data = {
    		"data": attractions
		}
		if has_more_data:
			response_data["nextPage"] = page + 1
		else:
			response_data["nextPage"] = None
		return jsonify(response_data)
	
	except mysql.connector.Error as error:
		return jsonify({"error": True, "message": f"伺服器內部錯誤: {str(error)}"})

	finally:
		if cursor:
			cursor.close()
			con.close()

# 根據景點編號取得景點資料
@app.route("/api/attraction/<int:attractionId>")
def get_attraction(attractionId):
	cursor = None
	try:
		con = connection()
		cursor = con.cursor(dictionary = True)
		query = "SELECT * FROM Attraction WHERE id = %s"
		cursor.execute(query, (attractionId,))
		attraction = cursor.fetchone()
	
		if attraction:
			images_query = " SELECT image FROM Attraction_image WHERE attraction_id = %s "
			cursor.execute(images_query, (attractionId,))
			images = [row["image"] for row in cursor.fetchall()]
			attraction["images"] = images
			return jsonify({"data": attraction})
		else:
			return jsonify({"error":True, "message":"景點編號不正確"})

	except mysql.connector.Error as error:
		return jsonify({"error": True, "message": f"伺服器內部錯誤: {str(error)}"})

	finally:
		if cursor:
			cursor.close()
			con.close()

# 取得捷運站資料列表
@app.route("/api/mrts")
def mrts():
	cursor = None
	try:
		con = connection()
		cursor = con.cursor()
		query = " SELECT mrt, COUNT(*) AS num_attractions FROM Attraction GROUP BY mrt ORDER BY num_attractions DESC "
		cursor.execute(query)
		mrt_list = [row[0] for row in cursor.fetchall()]
		return jsonify({"data": mrt_list})  

	except mysql.connector.Error as error:
		return jsonify({"error": True, "message": f"伺服器內部錯誤: {str(error)}"})

	finally:
		if cursor:
			cursor.close()
			con.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 3000, debug = True)
    app.secret_key = "secret"