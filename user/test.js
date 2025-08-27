connection = createConnection();

function authenticateUser(connection, email, password) {
        return new Promise((resolve, reject) => {
            const query = `
                SELECT * FROM weathertop_users WHERE EMAIL = ? AND PASSWORD = ?
            `;
            db.get(query, [email, password], (err, row) => {
                if (err) return reject(err);
                if (row) {
                    resolve({
                        id: row.EMAIL,
                        first_name: row.FIRST_NAME,
                        last_name: row.LAST_NAME
                    });
                } else {
                    console.log("returning undefined in userStore.js");
                    resolve(null);
                }
            });
        });
    }




    function authenticateUserTest(connection, email, password) {
        cursor = connection.cursor()
        try {
            cursor.execute("SELECT * FROM weathertop_users WHERE EMAIL = ? AND PASSWORD = ?", (email, password))
            result = cursor.fetchone()
            if(result) {
                return {
                    "id": result[0],
                    "first_name": result[1],
                    "last_name": result[2]
                }
            } else {
                return None
            }
        }
            
    }