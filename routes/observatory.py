from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from observatory.sequence_parser import SequenceParser
from observatory.action_registry import ActionRegistry

from routes import get_observatory

router = APIRouter(prefix="/observatory", tags=["observatory"])

@router.get("/actions")
async def list_actions():
    return {"actions": ActionRegistry.list_actions()}



@router.post("/observatory/rituals/parse")
async def upload_ritual_route(
    file: UploadFile = File(...),
    dry_run: bool = False
):
    if not file.filename.endswith(('.yaml', '.yml')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a YAML file.")
    content = await file.read()
    yaml_string = content.decode("utf-8")
    try:
        parsed_builder = SequenceParser(yaml_string)
        if not dry_run:
            get_observatory().sequence_registry.add_sequence(parsed_builder)
            return {"status": "parsed"}
        else:
            parsed_sequence = parsed_builder.build()
            print(parsed_sequence)
            return {"status": "valid", "parsed_steps": len(parsed_sequence.steps)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse ritual: {e}")