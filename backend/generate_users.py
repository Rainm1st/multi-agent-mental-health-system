import pandas as pd
import random
import string

def generate_users(count=200):
    users = []
    for i in range(1, count + 1):
        user_id = f"MH-{1000 + i}"
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        # 规避方案：第一位生成 1-9，后五位生成 0-9
        # 这样密码永远不会以 0 开头，彻底解决 Excel 自动去 0 的问题
        first_digit = random.choice("123456789")
        rest_digits = ''.join(random.choices(string.digits, k=5))
        password = first_digit + rest_digits
        
        users.append({
            "user_id": user_id, 
            "username": username,
            "password": password
        })
    
    df = pd.DataFrame(users)
    df.to_excel("users_list.xlsx", index=False)
    print(f"成功生成 {count} 个用户，已保存至 users_list.xlsx")

if __name__ == "__main__":
    generate_users()
