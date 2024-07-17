import aiomysql
from aiomysql import Error

class DatabaseConnection:
    def __init__(self, loop):
        self.connection = None
        self.loop = loop  # Event loop needed for aiomysql

    async def get_connection(self):
        try:
            self.connection = await aiomysql.connect(
                host='nonprod-stan.cuuqnikjun1p.ap-south-1.rds.amazonaws.com',
                db='stage_stan',
                user='admin',
                password='Stan.321',
                loop=self.loop
            )
            print("Connection established successfully")
            return self.connection
        except Error as e:
            print(f"Error: '{e}'")
            return None

    async def fetch_data(self, query):
        cursor = None
        result = None
        try:
            cursor = await self.connection.cursor(aiomysql.DictCursor)
            await cursor.execute(query)
            result = await cursor.fetchall()
        except Error as e:
            print(f"Error during fetching data: '{e}'")
        finally:
            if cursor:
                await cursor.close()
        return result

    async def close_connection(self):
        if self.connection and not self.connection.closed:
            self.connection.close()
            print("Database connection closed")
        else:
            print("Connection was already closed or was never opened.")


