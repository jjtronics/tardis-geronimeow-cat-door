"""Validation independante avec lib3mf (3MF Consortium), pip install lib3mf."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import lib3mf
ROOT=Path(__file__).resolve().parent
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
w=lib3mf.get_wrapper()
results=[]
for path in sorted((ROOT/'3mf').glob('*.3mf'))+[ROOT/'assemblage_couleur_reference.3mf']:
    model=w.CreateModel();reader=model.QueryReader('3mf');reader.ReadFromFile(str(path))
    warnings=[reader.GetWarning(i) for i in range(reader.GetWarningCount())]
    assert not warnings,(path.name,warnings)
    it=model.GetMeshObjects();count=0
    while it.MoveNext():
        mesh=it.GetCurrentMeshObject();count+=1
        assert mesh.IsManifoldAndOriented(),(path.name,mesh.GetName())
        assert mesh.IsValid(),(path.name,mesh.GetName())
    materials=model.GetBaseMaterialGroups();assert materials.MoveNext()
    assert materials.GetCurrentBaseMaterialGroup().GetCount()==4
    with zipfile.ZipFile(path) as z:
        root=ET.fromstring(z.read('3D/3dmodel.model'))
        cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
        objects={o.attrib['id']:o for o in root.findall('m:resources/m:object',NS)}
        for part in cfg.findall('object/part'):
            if part.attrib['subtype']!='normal_part':continue  # volume de support
            metadata={m.attrib['key']:m.attrib['value'] for m in part.findall('metadata')}
            assert int(metadata['extruder'])==int(objects[part.attrib['id']].attrib['pindex'])+1
        assert root.attrib['unit']=='millimeter'
    results.append(dict(file=path.name,mesh_count=count,warnings=warnings,
                        manifold=True,color_slots=4,part_assignments_match=True))
report=dict(library='3MF Consortium lib3mf',version=list(w.GetLibraryVersion()),files=results,
            creality_print_ui_tested=False)
(ROOT/'controle_3mf.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
