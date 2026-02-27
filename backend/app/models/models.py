from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, text, Enum, Date
from sqlalchemy.orm import relationship
from app.core.database import Base

# --- NHÓM 1: USER ---
class Roles(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    users = relationship('Users', back_populates='role')

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    phone_number = Column(String(20), nullable=True)
    role_id = Column(Integer, ForeignKey('roles.id'), default=1)
    status = Column(Enum('active', 'banned'), default='active')
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    
    role = relationship("Roles", back_populates="users")
    conversations = relationship('Conversations', back_populates='owner')
    posts = relationship('ForumPosts', back_populates='owner')
    comments = relationship('ForumComments', back_populates='owner')
    likes = relationship('PostLikes', back_populates='user')
    reports_sent = relationship('Reports', foreign_keys='Reports.reporter_id', back_populates='reporter')
    reports_received = relationship('Reports', foreign_keys='Reports.reported_user_id', back_populates='reported_user')
    ban_logs = relationship('BanLogs', foreign_keys='BanLogs.user_id', back_populates='user')

class BanLogs(Base):
    __tablename__ = 'ban_logs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    banned_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    user = relationship('Users', foreign_keys=[user_id], back_populates='ban_logs')
    admin = relationship('Users', foreign_keys=[banned_by])

# --- NHÓM 2: CHAT AI ---
class Conversations(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=True)
    openai_thread_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    owner = relationship('Users', back_populates='conversations')
    messages = relationship('Messages', back_populates='conversation', cascade="all, delete-orphan")

class Messages(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    conversation = relationship('Conversations', back_populates='messages')

# --- NHÓM 3: FORUM ---
class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    status = Column(Enum('active', 'hidden'), default='active')
    posts = relationship('ForumPosts', back_populates='category')

class ForumPosts(Base):
    __tablename__ = 'forum_posts'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    status = Column(Enum('active', 'hidden', 'closed'), default='active')
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    
    owner = relationship('Users', back_populates='posts')
    category = relationship('Categories', back_populates='posts')
    comments = relationship('ForumComments', back_populates='post', cascade="all, delete-orphan")
    likes = relationship('PostLikes', back_populates='post', cascade="all, delete-orphan")
    reports = relationship('Reports', back_populates='post')

class ForumComments(Base):
    __tablename__ = 'forum_comments'
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('forum_posts.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('forum_comments.id', ondelete='CASCADE'), nullable=True)
    content = Column(Text, nullable=False)
    status = Column(Enum('visible', 'hidden'), default='visible')
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    
    post = relationship('ForumPosts', back_populates='comments')
    owner = relationship('Users', back_populates='comments')
    parent = relationship('ForumComments', remote_side=[id], back_populates='replies')
    replies = relationship('ForumComments', back_populates='parent', cascade="all, delete-orphan")
    reports = relationship('Reports', back_populates='comment')

# --- NHÓM 4: INTERACTION ---
class PostLikes(Base):
    __tablename__ = 'post_likes'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    post_id = Column(Integer, ForeignKey('forum_posts.id', ondelete='CASCADE'), primary_key=True)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    user = relationship('Users', back_populates='likes')
    post = relationship('ForumPosts', back_populates='likes')

    
class AdminActionLogs(Base):
    __tablename__ = 'admin_action_logs'
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(50), nullable=False)     # VD: "CHANGE_ROLE", "BAN_USER"
    target_id = Column(Integer, nullable=True)      # ID của đối tượng bị tác động (user_id, post_id...)
    details = Column(String(255), nullable=True)    # Mô tả chi tiết
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    # Quan hệ ngược lại với bảng Users (Admin thực hiện)
    admin = relationship('Users', foreign_keys=[admin_id])

class Reports(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reported_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    post_id = Column(Integer, ForeignKey('forum_posts.id'), nullable=True)
    comment_id = Column(Integer, ForeignKey('forum_comments.id'), nullable=True)
    reason = Column(Text, nullable=True)
    status = Column(Enum('pending', 'resolved', 'rejected'), default='pending')
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    
    reporter = relationship('Users', foreign_keys=[reporter_id], back_populates='reports_sent')
    reported_user = relationship('Users', foreign_keys=[reported_user_id], back_populates='reports_received')
    post = relationship('ForumPosts', back_populates='reports')
    comment = relationship('ForumComments', back_populates='reports')

    