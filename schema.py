"""
schema.py
"""

from typing import Literal, List

from pydantic import BaseModel, Field


class DialogueItem(BaseModel):
    """单个对话项"""
    speaker: Literal["Host (Jane)", "Guest"] = Field(
        ..., 
        description="对话者身份"
    )
    text: str = Field(
        ..., 
        description="对话内容"
    )
    
    def model_post_init(self, _):
        """转换中文说话者名称为英文"""
        if self.speaker == "小美":
            self.speaker = "Host (Jane)"
        elif self.speaker == "专家":
            self.speaker = "Guest"


class DialogueBase(BaseModel):
    """对话基类"""
    scratchpad: str = Field(default="", description="准备笔记")
    name_of_guest: str = Field(default="专家", description="嘉宾名称")
    dialogue: List[DialogueItem]


class ShortDialogue(DialogueBase):
    """简短对话（1-2分钟）"""
    dialogue: List[DialogueItem] = Field(
        ..., 
        description="对话列表，通常包含11-17个对话项"
    )


class MediumDialogue(DialogueBase):
    """中等长度对话（3-5分钟）"""
    dialogue: List[DialogueItem] = Field(
        ..., 
        description="对话列表，通常包含19-29个对话项"
    )
