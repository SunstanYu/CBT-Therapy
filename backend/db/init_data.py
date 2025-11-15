"""
初始化数据库和测试数据
"""
from backend.db.orm import SessionLocal, init_db
from backend.models.user import User


def create_test_user():
    """创建测试用户"""
    db = SessionLocal()
    try:
        # 检查是否已存在测试用户
        existing_user = db.query(User).filter(User.username == "test_user").first()
        if existing_user:
            print(f"测试用户已存在，ID: {existing_user.id}")
            return existing_user.id
        
        # 创建新用户
        user = User(username="test_user", email="test@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"创建测试用户成功，ID: {user.id}")
        return user.id
    except Exception as e:
        db.rollback()
        print(f"创建测试用户失败: {e}")
        return None
    finally:
        db.close()


if __name__ == "__main__":
    print("初始化数据库...")
    init_db()
    print("数据库初始化完成")
    
    print("\n创建测试用户...")
    user_id = create_test_user()
    if user_id:
        print(f"\n✅ 初始化完成！测试用户ID: {user_id}")
        print("你可以使用这个用户ID开始测试会话。")
    else:
        print("\n❌ 初始化失败")

