"""
This type stub file was generated by pyright.
"""

import torch
from dataclasses import dataclass
from typing import Dict, Optional
from torch import Tensor, nn

@dataclass
class ModelDimensions:
    n_mels: int
    n_audio_ctx: int
    n_audio_state: int
    n_audio_head: int
    n_audio_layer: int
    n_vocab: int
    n_text_ctx: int
    n_text_state: int
    n_text_head: int
    n_text_layer: int
    ...


class LayerNorm(nn.LayerNorm):
    def forward(self, x: Tensor) -> Tensor:
        ...
    


class Linear(nn.Linear):
    def forward(self, x: Tensor) -> Tensor:
        ...
    


class Conv1d(nn.Conv1d):
    ...


def sinusoids(length, channels, max_timescale=...): # -> Tensor:
    """Returns sinusoids for positional embedding"""
    ...

class MultiHeadAttention(nn.Module):
    def __init__(self, n_state: int, n_head: int) -> None:
        ...
    
    def forward(self, x: Tensor, xa: Optional[Tensor] = ..., mask: Optional[Tensor] = ..., kv_cache: Optional[dict] = ...): # -> tuple[Any, Tensor]:
        ...
    
    def qkv_attention(self, q: Tensor, k: Tensor, v: Tensor, mask: Optional[Tensor] = ...): # -> tuple[Tensor, Tensor]:
        ...
    


class ResidualAttentionBlock(nn.Module):
    def __init__(self, n_state: int, n_head: int, cross_attention: bool = ...) -> None:
        ...
    
    def forward(self, x: Tensor, xa: Optional[Tensor] = ..., mask: Optional[Tensor] = ..., kv_cache: Optional[dict] = ...): # -> Tensor:
        ...
    


class AudioEncoder(nn.Module):
    def __init__(self, n_mels: int, n_ctx: int, n_state: int, n_head: int, n_layer: int) -> None:
        ...
    
    def forward(self, x: Tensor): # -> Tensor:
        """
        x : torch.Tensor, shape = (batch_size, n_mels, n_ctx)
            the mel spectrogram of the audio
        """
        ...
    


class TextDecoder(nn.Module):
    def __init__(self, n_vocab: int, n_ctx: int, n_state: int, n_head: int, n_layer: int) -> None:
        ...
    
    def forward(self, x: Tensor, xa: Tensor, kv_cache: Optional[dict] = ...): # -> Tensor:
        """
        x : torch.LongTensor, shape = (batch_size, <= n_ctx)
            the text tokens
        xa : torch.Tensor, shape = (batch_size, n_audio_ctx, n_audio_state)
            the encoded audio features to be attended on
        """
        ...
    


class Whisper(nn.Module):
    def __init__(self, dims: ModelDimensions) -> None:
        ...
    
    def set_alignment_heads(self, dump: bytes): # -> None:
        ...
    
    def embed_audio(self, mel: torch.Tensor): # -> Any:
        ...
    
    def logits(self, tokens: torch.Tensor, audio_features: torch.Tensor): # -> Any:
        ...
    
    def forward(self, mel: torch.Tensor, tokens: torch.Tensor) -> Dict[str, torch.Tensor]:
        ...
    
    @property
    def device(self): # -> device:
        ...
    
    @property
    def is_multilingual(self): # -> bool:
        ...
    
    @property
    def num_languages(self): # -> int:
        ...
    
    def install_kv_cache_hooks(self, cache: Optional[dict] = ...): # -> tuple[dict[Any, Any], list[Any]]:
        """
        The `MultiHeadAttention` module optionally accepts `kv_cache` which stores the key and value
        tensors calculated for the previous positions. This method returns a dictionary that stores
        all caches, and the necessary hooks for the key and value projection modules that save the
        intermediate tensors to be reused during later calculations.

        Returns
        -------
        cache : Dict[nn.Module, torch.Tensor]
            A dictionary object mapping the key/value projection modules to its cache
        hooks : List[RemovableHandle]
            List of PyTorch RemovableHandle objects to stop the hooks to be called
        """
        ...
    


