# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: rcon.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import referee_pb2
import game_event_pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='rcon.proto',
  package='',
  serialized_pb=_b('\n\nrcon.proto\x1a\rreferee.proto\x1a\x10game_event.proto\"\xb6\x04\n\x1fSSL_RefereeRemoteControlRequest\x12\x12\n\nmessage_id\x18\x01 \x02(\r\x12!\n\x05stage\x18\x02 \x01(\x0e\x32\x12.SSL_Referee.Stage\x12%\n\x07\x63ommand\x18\x03 \x01(\x0e\x32\x14.SSL_Referee.Command\x12/\n\x13\x64\x65signated_position\x18\x04 \x01(\x0b\x32\x12.SSL_Referee.Point\x12\x37\n\x04\x63\x61rd\x18\x05 \x01(\x0b\x32).SSL_RefereeRemoteControlRequest.CardInfo\x12\x1c\n\x14last_command_counter\x18\x06 \x01(\r\x12\x19\n\x11implementation_id\x18\x07 \x01(\t\x12*\n\tgameEvent\x18\x08 \x01(\x0b\x32\x17.SSL_Referee_Game_Event\x1a\xe5\x01\n\x08\x43\x61rdInfo\x12@\n\x04type\x18\x01 \x02(\x0e\x32\x32.SSL_RefereeRemoteControlRequest.CardInfo.CardType\x12@\n\x04team\x18\x02 \x02(\x0e\x32\x32.SSL_RefereeRemoteControlRequest.CardInfo.CardTeam\")\n\x08\x43\x61rdType\x12\x0f\n\x0b\x43\x41RD_YELLOW\x10\x00\x12\x0c\n\x08\x43\x41RD_RED\x10\x01\"*\n\x08\x43\x61rdTeam\x12\x0f\n\x0bTEAM_YELLOW\x10\x00\x12\r\n\tTEAM_BLUE\x10\x01\"\xa5\x02\n\x1dSSL_RefereeRemoteControlReply\x12\x12\n\nmessage_id\x18\x01 \x02(\r\x12\x37\n\x07outcome\x18\x02 \x02(\x0e\x32&.SSL_RefereeRemoteControlReply.Outcome\"\xb6\x01\n\x07Outcome\x12\x06\n\x02OK\x10\x00\x12\x14\n\x10MULTIPLE_ACTIONS\x10\x01\x12\r\n\tBAD_STAGE\x10\x02\x12\x0f\n\x0b\x42\x41\x44_COMMAND\x10\x03\x12\x1b\n\x17\x42\x41\x44_DESIGNATED_POSITION\x10\x04\x12\x17\n\x13\x42\x41\x44_COMMAND_COUNTER\x10\x05\x12\x0c\n\x08\x42\x41\x44_CARD\x10\x06\x12\x0f\n\x0bNO_MAJORITY\x10\x07\x12\x18\n\x14\x43OMMUNICATION_FAILED\x10\x08')
  ,
  dependencies=[referee_pb2.DESCRIPTOR,game_event_pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO_CARDTYPE = _descriptor.EnumDescriptor(
  name='CardType',
  full_name='SSL_RefereeRemoteControlRequest.CardInfo.CardType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='CARD_YELLOW', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CARD_RED', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=529,
  serialized_end=570,
)
_sym_db.RegisterEnumDescriptor(_SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO_CARDTYPE)

_SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO_CARDTEAM = _descriptor.EnumDescriptor(
  name='CardTeam',
  full_name='SSL_RefereeRemoteControlRequest.CardInfo.CardTeam',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='TEAM_YELLOW', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TEAM_BLUE', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=572,
  serialized_end=614,
)
_sym_db.RegisterEnumDescriptor(_SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO_CARDTEAM)

_SSL_REFEREEREMOTECONTROLREPLY_OUTCOME = _descriptor.EnumDescriptor(
  name='Outcome',
  full_name='SSL_RefereeRemoteControlReply.Outcome',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='OK', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='MULTIPLE_ACTIONS', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BAD_STAGE', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BAD_COMMAND', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BAD_DESIGNATED_POSITION', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BAD_COMMAND_COUNTER', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BAD_CARD', index=6, number=6,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NO_MAJORITY', index=7, number=7,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='COMMUNICATION_FAILED', index=8, number=8,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=728,
  serialized_end=910,
)
_sym_db.RegisterEnumDescriptor(_SSL_REFEREEREMOTECONTROLREPLY_OUTCOME)


_SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO = _descriptor.Descriptor(
  name='CardInfo',
  full_name='SSL_RefereeRemoteControlRequest.CardInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='SSL_RefereeRemoteControlRequest.CardInfo.type', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='team', full_name='SSL_RefereeRemoteControlRequest.CardInfo.team', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO_CARDTYPE,
    _SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO_CARDTEAM,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=385,
  serialized_end=614,
)

_SSL_REFEREEREMOTECONTROLREQUEST = _descriptor.Descriptor(
  name='SSL_RefereeRemoteControlRequest',
  full_name='SSL_RefereeRemoteControlRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message_id', full_name='SSL_RefereeRemoteControlRequest.message_id', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='stage', full_name='SSL_RefereeRemoteControlRequest.stage', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='command', full_name='SSL_RefereeRemoteControlRequest.command', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='designated_position', full_name='SSL_RefereeRemoteControlRequest.designated_position', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='card', full_name='SSL_RefereeRemoteControlRequest.card', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='last_command_counter', full_name='SSL_RefereeRemoteControlRequest.last_command_counter', index=5,
      number=6, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='implementation_id', full_name='SSL_RefereeRemoteControlRequest.implementation_id', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gameEvent', full_name='SSL_RefereeRemoteControlRequest.gameEvent', index=7,
      number=8, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=48,
  serialized_end=614,
)


_SSL_REFEREEREMOTECONTROLREPLY = _descriptor.Descriptor(
  name='SSL_RefereeRemoteControlReply',
  full_name='SSL_RefereeRemoteControlReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message_id', full_name='SSL_RefereeRemoteControlReply.message_id', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='outcome', full_name='SSL_RefereeRemoteControlReply.outcome', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _SSL_REFEREEREMOTECONTROLREPLY_OUTCOME,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=617,
  serialized_end=910,
)

_SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO.fields_by_name['type'].enum_type = _SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO_CARDTYPE
_SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO.fields_by_name['team'].enum_type = _SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO_CARDTEAM
_SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO.containing_type = _SSL_REFEREEREMOTECONTROLREQUEST
_SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO_CARDTYPE.containing_type = _SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO
_SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO_CARDTEAM.containing_type = _SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO
_SSL_REFEREEREMOTECONTROLREQUEST.fields_by_name['stage'].enum_type = referee_pb2._SSL_REFEREE_STAGE
_SSL_REFEREEREMOTECONTROLREQUEST.fields_by_name['command'].enum_type = referee_pb2._SSL_REFEREE_COMMAND
_SSL_REFEREEREMOTECONTROLREQUEST.fields_by_name['designated_position'].message_type = referee_pb2._SSL_REFEREE_POINT
_SSL_REFEREEREMOTECONTROLREQUEST.fields_by_name['card'].message_type = _SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO
_SSL_REFEREEREMOTECONTROLREQUEST.fields_by_name['gameEvent'].message_type = game_event_pb2._SSL_REFEREE_GAME_EVENT
_SSL_REFEREEREMOTECONTROLREPLY.fields_by_name['outcome'].enum_type = _SSL_REFEREEREMOTECONTROLREPLY_OUTCOME
_SSL_REFEREEREMOTECONTROLREPLY_OUTCOME.containing_type = _SSL_REFEREEREMOTECONTROLREPLY
DESCRIPTOR.message_types_by_name['SSL_RefereeRemoteControlRequest'] = _SSL_REFEREEREMOTECONTROLREQUEST
DESCRIPTOR.message_types_by_name['SSL_RefereeRemoteControlReply'] = _SSL_REFEREEREMOTECONTROLREPLY

SSL_RefereeRemoteControlRequest = _reflection.GeneratedProtocolMessageType('SSL_RefereeRemoteControlRequest', (_message.Message,), dict(

  CardInfo = _reflection.GeneratedProtocolMessageType('CardInfo', (_message.Message,), dict(
    DESCRIPTOR = _SSL_REFEREEREMOTECONTROLREQUEST_CARDINFO,
    __module__ = 'rcon_pb2'
    # @@protoc_insertion_point(class_scope:SSL_RefereeRemoteControlRequest.CardInfo)
    ))
  ,
  DESCRIPTOR = _SSL_REFEREEREMOTECONTROLREQUEST,
  __module__ = 'rcon_pb2'
  # @@protoc_insertion_point(class_scope:SSL_RefereeRemoteControlRequest)
  ))
_sym_db.RegisterMessage(SSL_RefereeRemoteControlRequest)
_sym_db.RegisterMessage(SSL_RefereeRemoteControlRequest.CardInfo)

SSL_RefereeRemoteControlReply = _reflection.GeneratedProtocolMessageType('SSL_RefereeRemoteControlReply', (_message.Message,), dict(
  DESCRIPTOR = _SSL_REFEREEREMOTECONTROLREPLY,
  __module__ = 'rcon_pb2'
  # @@protoc_insertion_point(class_scope:SSL_RefereeRemoteControlReply)
  ))
_sym_db.RegisterMessage(SSL_RefereeRemoteControlReply)


# @@protoc_insertion_point(module_scope)
