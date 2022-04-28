# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass

class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return f"<Username: {self.username}>"

class Player(db.Model):
    __tablename__ = 'players'
    
    player_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    gender = db.Column(db.String, nullable=True)
    # tier = relationship("PlayerTier")
    # game = relationship("Game", back_populates="player")
    
    # def __init__(self, player_id, name, gender):
    #     self.player_id = player_id
    #     self.name = name
    #     self.gender = gender
        
    def __repr__(self):
        return f"<Player name: {self.name}>"

class Venue(db.Model):
    __tablename__ = 'venues'
    
    venue_id = db.Column(db.Integer, primary_key=True)
    venue_name = db.Column(db.String)
    floor_type = db.Column(db.String)
    
    def __repr__(self):
        return f"<Venue name: {self.venue_name}>"

class Social(db.Model):
    __tablename__ = 'socials'
    
    social_id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.venue_id"))
    social_name = db.Column(db.String)
    social_weekday = db.Column(db.String)
    social_time = db.Column(db.String)
    doubles = db.Column(db.Integer, default=1)
    social_skill_levels = db.Column(db.String, default='open')
    
    # game = relationship("Game", back_populates="social")
    
    def __repr__(self):
        return f"<Social name: {self.social_name}>"

class Game(db.Model):
    __tablename__ = 'games'
    
    game_id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.Integer, db.ForeignKey("socials.social_id"))
    player_id = db.Column(db.Integer, db.ForeignKey("players.player_id"))
    game_type = db.Column(db.String)
    win = db.Column(db.Integer)
    played_date = db.Column(db.DateTime(timezone=True))
    
    # player = relationship("Player", back_populates="game")
    # social = relationship("Social", back_populates="game")
    
    def __repr__(self):
        return f"<Game type: {self.game_type}>"

# Separate player tiers table because tiers can change over time
# and because not every socials may use tiers
class PlayerTier(db.Model):
    __tablename__ = 'player_tiers'
    tier_id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.player_id"), primary_key=True)
    tier = db.Column(db.Integer)
    updated_at_date = db.Column(db.DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Tier: {self.tier}>"

@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
