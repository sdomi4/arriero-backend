from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Body
from observatory.sequence_parser import SequenceParser
from observatory.action_registry import ActionRegistry
from observatory.observatory import Observatory
from pydantic import BaseModel, ConfigDict, Field
from routes import get_observatory

class StartSequenceRequest(BaseModel):
    params: Dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="forbid")

router = APIRouter(prefix="/observatory", tags=["observatory"])

@router.get("/actions")
async def list_actions():
    return {"actions": ActionRegistry.list_actions()}

@router.get("/sequences")
async def list_sequences(observatory: Observatory = Depends(get_observatory)):
    return {"sequences": observatory.sequence_registry.list_sequences()}

@router.get("/sequences/active")
async def list_active_sequences(observatory: Observatory = Depends(get_observatory)):
    return {"active_sequences": list(observatory.state.snapshot().sequences.values())}

@router.post("/sequences/{sequence}/run")
async def run_sequence(
    sequence: str,
    observatory: Observatory = Depends(get_observatory),
    body: Optional[StartSequenceRequest] = Body(None)
):
    sequence_builder = observatory.sequence_registry.sequences.get(sequence)
    if not sequence_builder:
        raise HTTPException(status_code=404, detail=f"Sequence '{sequence}' not found.")
    params = body.params if body else {}
    context_id = observatory.sequence_registry.run_sequence(observatory, sequence_builder, **params)
    observatory.state.add_sequence(context_id, sequence)
    return {"context_id": context_id}

@router.post("/sequences/{context_id}/pause")
async def pause_sequence(context_id: str, observatory: Observatory = Depends(get_observatory)):
    if context_id not in observatory.state.snapshot().sequences:
        raise HTTPException(status_code=404, detail=f"Sequence with context_id '{context_id}' not found.")
    observatory.sequence_registry.registry[context_id][1].request_pause() # access context instance and pause
    return {"status": "paused"}

@router.post("/sequences/{context_id}/resume")
async def resume_sequence(context_id: str, observatory: Observatory = Depends(get_observatory)):
    if context_id not in observatory.state.snapshot().sequences:
        raise HTTPException(status_code=404, detail=f"Sequence with context_id '{context_id}' not found.")
    observatory.sequence_registry.registry[context_id][1].resume() # access context instance and resume
    return {"status": "resumed"}

@router.post("/sequences/{context_id}/abort")
async def abort_sequence(context_id: str, observatory: Observatory = Depends(get_observatory)):
    if context_id not in observatory.state.snapshot().sequences:
        raise HTTPException(status_code=404, detail=f"Sequence with context_id '{context_id}' not found.")
    observatory.sequence_registry.registry[context_id][1].abort() # access context instance and abort
    return {"status": "aborted"}

@router.post("/sequences/parse")
async def upload_sequence(
    file: UploadFile = File(...),
    dry_run: bool = False,
    observatory: Observatory = Depends(get_observatory)
):
    if not file.filename.endswith(('.yaml', '.yml')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a YAML file.")
    content = await file.read()
    yaml_string = content.decode("utf-8")
    try:
        parsed_builder = SequenceParser(yaml_string)
        if not dry_run:
            observatory.sequence_registry.add_sequence(parsed_builder)
            return {"status": "parsed"}
        else:
            parsed_sequence = parsed_builder.build()
            print(parsed_sequence)
            return {"status": "valid", "parsed_steps": len(parsed_sequence.steps)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse sequence: {e}")