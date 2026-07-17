from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import time
import urllib.request
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "TASK-199"
CAMPAIGN_NAME = "WDI External Debt Large Chunked Expansion Campaign"
CAMPAIGN_MODE = "Large Campaign Execution Optimization"
SOURCE_NAME = "World Bank World Development Indicators external debt indicators"
COUNTRY_CATALOG_FIXTURE = PROJECT_ROOT / "data/raw/wdi_operational_phase1/wdi-phase1-all-countries-3i-2000-2023.json"
BASE_RAW_DIR = PROJECT_ROOT / "data/raw/task199_wdi_external_debt_chunked_expansion"
BASE_PROCESSED_DIR = PROJECT_ROOT / "data/processed/task199_wdi_external_debt_chunked_expansion"
CHECKPOINT_DIR = BASE_RAW_DIR / "checkpoints"
RAW_CHUNK_DIR = BASE_RAW_DIR / "chunks"
NORM_CHUNK_DIR = BASE_PROCESSED_DIR / "chunks"
MANIFEST_PATH = BASE_PROCESSED_DIR / "task-199-wdi-external-debt-chunked-manifest.json"
DATE_RANGE = "1990:2024"
PERIODS = [str(y) for y in range(1990, 2025)]
CHUNK_SIZE = 80
CANDIDATE_INDICATORS = [
    "BX.GRT.EXTA.CD.DT",
    "BX.GRT.TECH.CD.DT",
    "BX.KLT.DINV.CD.DT",
    "BX.KLT.DREM.CD.DT",
    "BX.PEF.TOTL.CD.DT",
    "DT.AMT.BLAT.CD",
    "DT.AMT.BLAT.GG.CD",
    "DT.AMT.BLAT.OPS.CD",
    "DT.AMT.BLAT.PRVG.CD",
    "DT.AMT.BLAT.PS.CD",
    "DT.AMT.BLTC.CD",
    "DT.AMT.BLTC.GG.CD",
    "DT.AMT.BLTC.OPS.CD",
    "DT.AMT.BLTC.PRVG.CD",
    "DT.AMT.BLTC.PS.CD",
    "DT.AMT.DEGG.CD",
    "DT.AMT.DEPS.CD",
    "DT.AMT.DIMF.CD",
    "DT.AMT.DLTF.CD",
    "DT.AMT.DLXF.CD",
    "DT.AMT.DOPS.CD",
    "DT.AMT.DPNG.CD",
    "DT.AMT.DPPG.CD",
    "DT.AMT.MIBR.CD",
    "DT.AMT.MIDA.CD",
    "DT.AMT.MLAT.CD",
    "DT.AMT.MLAT.GG.CD",
    "DT.AMT.MLAT.OPS.CD",
    "DT.AMT.MLAT.PRVG.CD",
    "DT.AMT.MLAT.PS.CD",
    "DT.AMT.MLTC.CD",
    "DT.AMT.MLTC.GG.CD",
    "DT.AMT.MLTC.OPS.CD",
    "DT.AMT.MLTC.PRVG.CD",
    "DT.AMT.MLTC.PS.CD",
    "DT.AMT.OFFT.CD",
    "DT.AMT.OFFT.GG.CD",
    "DT.AMT.OFFT.OPS.CD",
    "DT.AMT.OFFT.PRVG.CD",
    "DT.AMT.OFFT.PS.CD",
    "DT.AMT.PBND.CD",
    "DT.AMT.PBND.GG.CD",
    "DT.AMT.PBND.OPS.CD",
    "DT.AMT.PBND.PRVG.CD",
    "DT.AMT.PBND.PS.CD",
    "DT.AMT.PCBK.CD",
    "DT.AMT.PCBK.GG.CD",
    "DT.AMT.PCBK.OPS.CD",
    "DT.AMT.PCBK.PRVG.CD",
    "DT.AMT.PCBK.PS.CD",
    "DT.AMT.PNGB.CD",
    "DT.AMT.PNGC.CD",
    "DT.AMT.PROP.CD",
    "DT.AMT.PROP.GG.CD",
    "DT.AMT.PROP.OPS.CD",
    "DT.AMT.PROP.PRVG.CD",
    "DT.AMT.PROP.PS.CD",
    "DT.AMT.PRPG.CD",
    "DT.AMT.PRVT.CD",
    "DT.AMT.PRVT.GG.CD",
    "DT.AMT.PRVT.OPS.CD",
    "DT.AMT.PRVT.PRVG.CD",
    "DT.AMT.PRVT.PS.CD",
    "DT.AXA.DPPG.CD",
    "DT.AXA.OFFT.CD",
    "DT.AXA.PRVT.CD",
    "DT.AXF.DPPG.CD",
    "DT.AXR.DPPG.CD",
    "DT.AXR.OFFT.CD",
    "DT.AXR.PRVT.CD",
    "DT.COM.BLAT.CD",
    "DT.COM.DPPG.CD",
    "DT.COM.MIBR.CD",
    "DT.COM.MIDA.CD",
    "DT.COM.MLAT.CD",
    "DT.COM.OFFT.CD",
    "DT.COM.PRVT.CD",
    "DT.CUR.DMAK.ZS",
    "DT.CUR.EURO.ZS",
    "DT.CUR.FFRC.ZS",
    "DT.CUR.JYEN.ZS",
    "DT.CUR.MULC.ZS",
    "DT.CUR.OTHC.ZS",
    "DT.CUR.SDRW.ZS",
    "DT.CUR.SWFR.ZS",
    "DT.CUR.UKPS.ZS",
    "DT.CUR.USDL.ZS",
    "DT.DFR.DPPG.CD",
    "DT.DIS.BLAT.CD",
    "DT.DIS.BLAT.GG.CD",
    "DT.DIS.BLAT.OPS.CD",
    "DT.DIS.BLAT.PRVG.CD",
    "DT.DIS.BLAT.PS.CD",
    "DT.DIS.BLTC.CD",
    "DT.DIS.BLTC.GG.CD",
    "DT.DIS.BLTC.OPS.CD",
    "DT.DIS.BLTC.PRVG.CD",
    "DT.DIS.BLTC.PS.CD",
    "DT.DIS.DEGG.CD",
    "DT.DIS.DEPS.CD",
    "DT.DIS.DIMF.CD",
    "DT.DIS.DLTF.CD",
    "DT.DIS.DLXF.CD",
    "DT.DIS.DOPS.CD",
    "DT.DIS.DPNG.CD",
    "DT.DIS.DPPG.CD",
    "DT.DIS.IDAG.CD",
    "DT.DIS.MIBR.CD",
    "DT.DIS.MIDA.CD",
    "DT.DIS.MLAT.CD",
    "DT.DIS.MLAT.GG.CD",
    "DT.DIS.MLAT.OPS.CD",
    "DT.DIS.MLAT.PRVG.CD",
    "DT.DIS.MLAT.PS.CD",
    "DT.DIS.MLTC.CD",
    "DT.DIS.MLTC.GG.CD",
    "DT.DIS.MLTC.OPS.CD",
    "DT.DIS.MLTC.PRVG.CD",
    "DT.DIS.MLTC.PS.CD",
    "DT.DIS.OFFT.CD",
    "DT.DIS.OFFT.GG.CD",
    "DT.DIS.OFFT.OPS.CD",
    "DT.DIS.OFFT.PRVG.CD",
    "DT.DIS.OFFT.PS.CD",
    "DT.DIS.PBND.CD",
    "DT.DIS.PBND.GG.CD",
    "DT.DIS.PBND.OPS.CD",
    "DT.DIS.PBND.PRVG.CD",
    "DT.DIS.PBND.PS.CD",
    "DT.DIS.PCBK.CD",
    "DT.DIS.PCBK.GG.CD",
    "DT.DIS.PCBK.OPS.CD",
    "DT.DIS.PCBK.PRVG.CD",
    "DT.DIS.PCBK.PS.CD",
    "DT.DIS.PNGB.CD",
    "DT.DIS.PNGC.CD",
    "DT.DIS.PROP.CD",
    "DT.DIS.PROP.GG.CD",
    "DT.DIS.PROP.OPS.CD",
    "DT.DIS.PROP.PRVG.CD",
    "DT.DIS.PROP.PS.CD",
    "DT.DIS.PRPG.CD",
    "DT.DIS.PRVT.CD",
    "DT.DIS.PRVT.GG.CD",
    "DT.DIS.PRVT.OPS.CD",
    "DT.DIS.PRVT.PRVG.CD",
    "DT.DIS.PRVT.PS.CD",
    "DT.DOD.ALLC.CD",
    "DT.DOD.ALLC.ZS",
    "DT.DOD.BLAT.CD",
    "DT.DOD.BLAT.GG.CD",
    "DT.DOD.BLAT.OPS.CD",
    "DT.DOD.BLAT.PRVG.CD",
    "DT.DOD.BLAT.PS.CD",
    "DT.DOD.BLTC.CD",
    "DT.DOD.BLTC.GG.CD",
    "DT.DOD.BLTC.OPS.CD",
    "DT.DOD.BLTC.PRVG.CD",
    "DT.DOD.BLTC.PS.CD",
    "DT.DOD.DECT.CD.CG",
    "DT.DOD.DECT.EX.ZS",
    "DT.DOD.DEGG.CD",
    "DT.DOD.DEPS.CD",
    "DT.DOD.DIMF.CD",
    "DT.DOD.DLXF.CD",
    "DT.DOD.DOPS.CD",
    "DT.DOD.DPNG.CD",
    "DT.DOD.DPPG.CD",
    "DT.DOD.DSDR.CD",
    "DT.DOD.DSTC.CD",
    "DT.DOD.DSTC.ZS",
    "DT.DOD.MDRI.CD",
    "DT.DOD.MIBR.CD",
    "DT.DOD.MIDA.CD",
    "DT.DOD.MLAT.CD",
    "DT.DOD.MLAT.GG.CD",
    "DT.DOD.MLAT.OPS.CD",
    "DT.DOD.MLAT.PRVG.CD",
    "DT.DOD.MLAT.PS.CD",
    "DT.DOD.MLAT.ZS",
    "DT.DOD.MLTC.CD",
    "DT.DOD.MLTC.GG.CD",
    "DT.DOD.MLTC.OPS.CD",
    "DT.DOD.MLTC.PRVG.CD",
    "DT.DOD.MLTC.PS.CD",
    "DT.DOD.MWBG.CD",
    "DT.DOD.OFFT.CD",
    "DT.DOD.OFFT.GG.CD",
    "DT.DOD.OFFT.OPS.CD",
    "DT.DOD.OFFT.PRVG.CD",
    "DT.DOD.OFFT.PS.CD",
    "DT.DOD.PBND.CD",
    "DT.DOD.PBND.GG.CD",
    "DT.DOD.PBND.OPS.CD",
    "DT.DOD.PBND.PRVG.CD",
    "DT.DOD.PBND.PS.CD",
    "DT.DOD.PCBK.CD",
    "DT.DOD.PCBK.GG.CD",
    "DT.DOD.PCBK.OPS.CD",
    "DT.DOD.PCBK.PRVG.CD",
    "DT.DOD.PCBK.PS.CD",
    "DT.DOD.PNGB.CD",
    "DT.DOD.PNGC.CD",
    "DT.DOD.PROP.CD",
    "DT.DOD.PROP.GG.CD",
    "DT.DOD.PROP.OPS.CD",
    "DT.DOD.PROP.PRVG.CD",
    "DT.DOD.PROP.PS.CD",
    "DT.DOD.PRPG.CD",
    "DT.DOD.PRVS.CD",
    "DT.DOD.PRVT.CD",
    "DT.DOD.PRVT.GG.CD",
    "DT.DOD.PRVT.OPS.CD",
    "DT.DOD.PRVT.PRVG.CD",
    "DT.DOD.PRVT.PS.CD",
    "DT.DOD.PUBS.CD",
    "DT.DOD.RSDL.CD",
    "DT.DOD.VTOT.CD",
    "DT.DSB.DPPG.CD",
    "DT.DSF.DPPG.CD",
    "DT.DXR.DPPG.CD",
    "DT.GPA.DPPG",
    "DT.GPA.OFFT",
    "DT.GPA.PRVT",
    "DT.GRE.DPPG",
    "DT.GRE.OFFT",
    "DT.GRE.PRVT",
    "DT.INR.DPPG",
    "DT.INR.OFFT",
    "DT.INR.PRVT",
    "DT.INT.BLAT.CD",
    "DT.INT.BLAT.GG.CD",
    "DT.INT.BLAT.OPS.CD",
    "DT.INT.BLAT.PRVG.CD",
    "DT.INT.BLAT.PS.CD",
    "DT.INT.BLTC.CD",
    "DT.INT.BLTC.GG.CD",
    "DT.INT.BLTC.OPS.CD",
    "DT.INT.BLTC.PRVG.CD",
    "DT.INT.BLTC.PS.CD",
    "DT.INT.DECT.CD",
    "DT.INT.DECT.EX.ZS",
    "DT.INT.DECT.GN.ZS",
    "DT.INT.DEGG.CD",
    "DT.INT.DEPS.CD",
    "DT.INT.DIMF.CD",
    "DT.INT.DLXF.CD",
    "DT.INT.DOPS.CD",
    "DT.INT.DPNG.CD",
    "DT.INT.DPPG.CD",
    "DT.INT.DSTC.CD",
    "DT.INT.MIBR.CD",
    "DT.INT.MIDA.CD",
    "DT.INT.MLAT.CD",
    "DT.INT.MLAT.GG.CD",
    "DT.INT.MLAT.OPS.CD",
    "DT.INT.MLAT.PRVG.CD",
    "DT.INT.MLAT.PS.CD",
    "DT.INT.MLTC.CD",
    "DT.INT.MLTC.GG.CD",
    "DT.INT.MLTC.OPS.CD",
    "DT.INT.MLTC.PRVG.CD",
    "DT.INT.MLTC.PS.CD",
    "DT.INT.OFFT.CD",
    "DT.INT.OFFT.GG.CD",
    "DT.INT.OFFT.OPS.CD",
    "DT.INT.OFFT.PRVG.CD",
    "DT.INT.OFFT.PS.CD",
    "DT.INT.PBND.CD",
    "DT.INT.PBND.GG.CD",
    "DT.INT.PBND.OPS.CD",
    "DT.INT.PBND.PRVG.CD",
    "DT.INT.PBND.PS.CD",
    "DT.INT.PCBK.CD",
    "DT.INT.PCBK.GG.CD",
    "DT.INT.PCBK.OPS.CD",
    "DT.INT.PCBK.PRVG.CD",
    "DT.INT.PCBK.PS.CD",
    "DT.INT.PNGB.CD",
    "DT.INT.PNGC.CD",
    "DT.INT.PROP.CD",
    "DT.INT.PROP.GG.CD",
    "DT.INT.PROP.OPS.CD",
    "DT.INT.PROP.PRVG.CD",
    "DT.INT.PROP.PS.CD",
    "DT.INT.PRPG.CD",
    "DT.INT.PRVT.CD",
    "DT.INT.PRVT.GG.CD",
    "DT.INT.PRVT.OPS.CD",
    "DT.INT.PRVT.PRVG.CD",
    "DT.INT.PRVT.PS.CD",
    "DT.IXA.DPPG.CD",
    "DT.IXA.DPPG.CD.CG",
    "DT.IXA.OFFT.CD",
    "DT.IXA.PRVT.CD",
    "DT.IXF.DPPG.CD",
    "DT.IXR.DPPG.CD",
    "DT.IXR.OFFT.CD",
    "DT.IXR.PRVT.CD",
    "DT.MAT.DPPG",
    "DT.MAT.OFFT",
    "DT.MAT.PRVT",
    "DT.NFL.BLAT.CD",
    "DT.NFL.BLAT.GG.CD",
    "DT.NFL.BLAT.OPS.CD",
    "DT.NFL.BLAT.PRVG.CD",
    "DT.NFL.BLAT.PS.CD",
    "DT.NFL.BLTC.CD",
    "DT.NFL.BLTC.GG.CD",
    "DT.NFL.BLTC.OPS.CD",
    "DT.NFL.BLTC.PRVG.CD",
    "DT.NFL.BLTC.PS.CD",
    "DT.NFL.BOND.CD",
    "DT.NFL.DECT.CD",
    "DT.NFL.DEGG.CD",
    "DT.NFL.DEPS.CD",
    "DT.NFL.DLXF.CD",
    "DT.NFL.DOPS.CD",
    "DT.NFL.DPNG.CD",
    "DT.NFL.DPPG.CD",
    "DT.NFL.DSTC.CD",
    "DT.NFL.IMFC.CD",
    "DT.NFL.IMFN.CD",
    "DT.NFL.MIBR.CD",
    "DT.NFL.MIDA.CD",
    "DT.NFL.MLAT.CD",
    "DT.NFL.MLAT.GG.CD",
    "DT.NFL.MLAT.OPS.CD",
    "DT.NFL.MLAT.PRVG.CD",
    "DT.NFL.MLAT.PS.CD",
    "DT.NFL.MLTC.CD",
    "DT.NFL.MLTC.GG.CD",
    "DT.NFL.MLTC.OPS.CD",
    "DT.NFL.MLTC.PRVG.CD",
    "DT.NFL.MLTC.PS.CD",
    "DT.NFL.MOTH.CD",
    "DT.NFL.NEBR.CD",
    "DT.NFL.NIFC.CD",
    "DT.NFL.OFFT.CD",
    "DT.NFL.OFFT.GG.CD",
    "DT.NFL.OFFT.OPS.CD",
    "DT.NFL.OFFT.PRVG.CD",
    "DT.NFL.OFFT.PS.CD",
    "DT.NFL.PBND.CD",
    "DT.NFL.PBND.GG.CD",
    "DT.NFL.PBND.OPS.CD",
    "DT.NFL.PBND.PRVG.CD",
    "DT.NFL.PBND.PS.CD",
    "DT.NFL.PCBK.CD",
    "DT.NFL.PCBK.GG.CD",
    "DT.NFL.PCBK.OPS.CD",
    "DT.NFL.PCBK.PRVG.CD",
    "DT.NFL.PCBK.PS.CD",
    "DT.NFL.PCBO.CD",
    "DT.NFL.PNGB.CD",
    "DT.NFL.PNGC.CD",
    "DT.NFL.PROP.CD",
    "DT.NFL.PROP.GG.CD",
    "DT.NFL.PROP.OPS.CD",
    "DT.NFL.PROP.PRVG.CD",
    "DT.NFL.PROP.PS.CD",
    "DT.NFL.PRPG.CD",
    "DT.NFL.PRVT.CD",
    "DT.NFL.PRVT.GG.CD",
    "DT.NFL.PRVT.OPS.CD",
    "DT.NFL.PRVT.PRVG.CD",
    "DT.NFL.PRVT.PS.CD",
    "DT.NFL.RDBC.CD",
    "DT.NFL.RDBN.CD",
    "DT.NTR.BLAT.CD",
    "DT.NTR.BLAT.GG.CD",
    "DT.NTR.BLAT.OPS.CD",
    "DT.NTR.BLAT.PRVG.CD",
    "DT.NTR.BLAT.PS.CD",
    "DT.NTR.BLTC.CD",
    "DT.NTR.BLTC.GG.CD",
    "DT.NTR.BLTC.OPS.CD",
    "DT.NTR.BLTC.PRVG.CD",
    "DT.NTR.BLTC.PS.CD",
    "DT.NTR.DECT.CD",
    "DT.NTR.DEGG.CD",
    "DT.NTR.DEPS.CD",
    "DT.NTR.DLXF.CD",
    "DT.NTR.DOPS.CD",
    "DT.NTR.DPNG.CD",
    "DT.NTR.DPPG.CD",
    "DT.NTR.MIBR.CD",
    "DT.NTR.MIDA.CD",
    "DT.NTR.MLAT.CD",
    "DT.NTR.MLAT.GG.CD",
    "DT.NTR.MLAT.OPS.CD",
    "DT.NTR.MLAT.PRVG.CD",
    "DT.NTR.MLAT.PS.CD",
    "DT.NTR.MLTC.CD",
    "DT.NTR.MLTC.GG.CD",
    "DT.NTR.MLTC.OPS.CD",
    "DT.NTR.MLTC.PRVG.CD",
    "DT.NTR.MLTC.PS.CD",
    "DT.NTR.OFFT.CD",
    "DT.NTR.OFFT.GG.CD",
    "DT.NTR.OFFT.OPS.CD",
    "DT.NTR.OFFT.PRVG.CD",
    "DT.NTR.OFFT.PS.CD",
    "DT.NTR.PBND.CD",
    "DT.NTR.PBND.GG.CD",
    "DT.NTR.PBND.OPS.CD",
    "DT.NTR.PBND.PRVG.CD",
    "DT.NTR.PBND.PS.CD",
    "DT.NTR.PCBK.CD",
    "DT.NTR.PCBK.GG.CD",
    "DT.NTR.PCBK.OPS.CD",
    "DT.NTR.PCBK.PRVG.CD",
    "DT.NTR.PCBK.PS.CD",
    "DT.NTR.PNGB.CD",
    "DT.NTR.PNGC.CD",
    "DT.NTR.PROP.CD",
    "DT.NTR.PROP.GG.CD",
    "DT.NTR.PROP.OPS.CD",
    "DT.NTR.PROP.PRVG.CD",
    "DT.NTR.PROP.PS.CD",
    "DT.NTR.PRPG.CD",
    "DT.NTR.PRVT.CD",
    "DT.NTR.PRVT.GG.CD",
    "DT.NTR.PRVT.OPS.CD",
    "DT.NTR.PRVT.PRVG.CD",
    "DT.NTR.PRVT.PS.CD",
    "DT.TDS.BLAT.CD",
    "DT.TDS.BLAT.GG.CD",
    "DT.TDS.BLAT.OPS.CD",
    "DT.TDS.BLAT.PRVG.CD",
    "DT.TDS.BLAT.PS.CD",
    "DT.TDS.BLTC.CD",
    "DT.TDS.BLTC.GG.CD",
    "DT.TDS.BLTC.OPS.CD",
    "DT.TDS.BLTC.PRVG.CD",
    "DT.TDS.BLTC.PS.CD",
    "DT.TDS.DECT.CD",
    "DT.TDS.DEGG.CD",
    "DT.TDS.DEPS.CD",
    "DT.TDS.DIMF.CD",
    "DT.TDS.DLXF.CD",
    "DT.TDS.DOPS.CD",
    "DT.TDS.DPNG.CD",
    "DT.TDS.DPPF.XP.ZS",
    "DT.TDS.DPPG.CD",
    "DT.TDS.DPPG.GN.ZS",
    "DT.TDS.DPPG.XP.ZS",
    "DT.TDS.MIBR.CD",
    "DT.TDS.MIDA.CD",
    "DT.TDS.MLAT.CD",
    "DT.TDS.MLAT.GG.CD",
    "DT.TDS.MLAT.OPS.CD",
    "DT.TDS.MLAT.PG.ZS",
    "DT.TDS.MLAT.PRVG.CD",
    "DT.TDS.MLAT.PS.CD",
    "DT.TDS.MLTC.CD",
    "DT.TDS.MLTC.GG.CD",
    "DT.TDS.MLTC.OPS.CD",
    "DT.TDS.MLTC.PRVG.CD",
    "DT.TDS.MLTC.PS.CD",
    "DT.TDS.OFFT.CD",
    "DT.TDS.OFFT.GG.CD",
    "DT.TDS.OFFT.OPS.CD",
    "DT.TDS.OFFT.PRVG.CD",
    "DT.TDS.OFFT.PS.CD",
    "DT.TDS.PBND.CD",
    "DT.TDS.PBND.GG.CD",
    "DT.TDS.PBND.OPS.CD",
    "DT.TDS.PBND.PRVG.CD",
    "DT.TDS.PBND.PS.CD",
    "DT.TDS.PCBK.CD",
    "DT.TDS.PCBK.GG.CD",
    "DT.TDS.PCBK.OPS.CD",
    "DT.TDS.PCBK.PRVG.CD",
    "DT.TDS.PCBK.PS.CD",
    "DT.TDS.PNGB.CD",
    "DT.TDS.PNGC.CD",
    "DT.TDS.PROP.CD",
    "DT.TDS.PROP.GG.CD",
    "DT.TDS.PROP.OPS.CD",
    "DT.TDS.PROP.PRVG.CD",
    "DT.TDS.PROP.PS.CD",
    "DT.TDS.PRPG.CD",
    "DT.TDS.PRVT.CD",
    "DT.TDS.PRVT.GG.CD",
    "DT.TDS.PRVT.OPS.CD",
    "DT.TDS.PRVT.PRVG.CD",
    "DT.TDS.PRVT.PS.CD",
    "DT.TXR.DPPG.CD",
    "DT.UND.DPPG.CD",
    "DT.UND.OFFT.CD",
    "DT.UND.PRVT.CD",
    "FI.RES.TOTL.DT.ZS"
]
NON_GOALS = ["architecture_redesign", "generic_WDI_framework_extraction", "provider_mirror", "source_registry", "production_live_ingestion", "raw_evidence_cleanup"]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_blob(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _file_sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def _load_countries() -> tuple[list[str], list[dict[str, Any]]]:
    raw = _read_json(COUNTRY_CATALOG_FIXTURE)
    countries = list(raw["scope"]["countries"])
    catalog = list(raw["country_catalog"]["countries"])
    by_id = {r["id"]: r for r in catalog}
    countries = [c for c in countries if c in by_id]
    aggregates = [r["id"] for r in catalog if r.get("region", {}).get("id") == "NA" and r["id"] in countries]
    if aggregates:
        raise ValueError(f"country catalog includes aggregate rows: {aggregates[:5]}")
    return countries, [by_id[c] for c in countries]


def _worldbank_url(indicator: str) -> str:
    return f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&date={DATE_RANGE}&per_page=20000"


def _indicator_metadata_url(indicator: str) -> str:
    return f"https://api.worldbank.org/v2/indicator/{indicator}?format=json"


def _get_json(url: str, timeout_seconds: int) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "MacroForge TASK-199 WDI external debt chunked expansion"})
    with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def _checkpoint_path(indicator: str) -> Path:
    safe = indicator.replace("/", "_").replace(":", "_")
    return CHECKPOINT_DIR / f"{safe}.json"


def _chunks(values: list[str], size: int) -> list[list[str]]:
    return [values[i:i+size] for i in range(0, len(values), size)]


def fetch_one(indicator: str, allowed: set[str], timeout_seconds: int) -> dict[str, Any]:
    cp = _checkpoint_path(indicator)
    if cp.exists():
        cached = _read_json(cp)
        cached["checkpoint_status"] = "resumed_from_checkpoint"
        return cached
    data_url = _worldbank_url(indicator)
    meta_url = _indicator_metadata_url(indicator)
    payload = None; metadata_payload = None; data_error = None; metadata_error = None
    start = time.monotonic()
    for _ in range(3):
        try:
            payload = _get_json(data_url, timeout_seconds)
            if isinstance(payload, list) and len(payload) == 2 and isinstance(payload[1], list):
                before_total = len(payload[1])
                payload = [dict(payload[0]), [r for r in payload[1] if r.get("countryiso3code") in allowed]]
                payload[0]["total_before_non_aggregate_filter"] = payload[0].get("total")
                payload[0]["rows_before_non_aggregate_filter"] = before_total
                payload[0]["total"] = len(payload[1])
            data_error = None; break
        except Exception as exc:
            data_error = {"type": type(exc).__name__, "message": str(exc)}
    for _ in range(3):
        try:
            metadata_payload = _get_json(meta_url, timeout_seconds)
            metadata_error = None; break
        except Exception as exc:
            metadata_error = {"type": type(exc).__name__, "message": str(exc)}
    if data_error is not None:
        payload = [{"error": data_error["type"], "message": data_error["message"], "lastupdated": None}, []]
    if metadata_error is not None:
        metadata_payload = [{"error": metadata_error["type"], "message": metadata_error["message"]}]
    result = {"indicator_code": indicator, "url": data_url, "metadata_url": meta_url, "response": payload, "metadata_response": metadata_payload, "checkpoint_status": "fetched_and_checkpointed", "elapsed_seconds": round(time.monotonic()-start, 3)}
    cp.parent.mkdir(parents=True, exist_ok=True)
    tmp=cp.with_suffix('.tmp')
    tmp.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(cp)
    return result


def base_scope(indicators: list[str], chunk_index: int | None = None) -> dict[str, Any]:
    countries, _ = _load_countries()
    return {"task": TASK_ID, "campaign": CAMPAIGN_NAME, "mode": CAMPAIGN_MODE,
        "strategic_objective": "construct the canonical macroeconomic repository while improving large campaign execution",
        "domain": "External debt and debt-service vulnerability", "analytical_capability": "External debt stocks, flows, debt service, creditor composition, concessionality, arrears, and reserve/debt vulnerability monitoring",
        "confidence_cell": "WDI public API v2 annual scalar country-indicator observations for external debt indicators",
        "country_scope": "all_non_aggregate_wdi_countries", "countries": countries, "country_count": len(countries),
        "date_range": DATE_RANGE, "periods": PERIODS, "indicators": indicators, "candidate_count": len(indicators),
        "max_presparsity_rows": len(countries) * len(PERIODS) * len(indicators), "chunk_index": chunk_index,
        "chunk_size": CHUNK_SIZE, "raw_evidence_policy": "preserve per-indicator checkpoints and per-chunk raw/normalized artifacts by default",
        "execution_improvements": ["per_indicator_atomic_checkpoints", "deterministic_candidate_chunks", "per_chunk_raw_artifacts", "per_chunk_normalized_artifacts", "partial_completion_manifest", "chunked_postgresql_loads"],
        "non_goals": NON_GOALS}


def fetch_raw(timeout_seconds: int = 45, max_workers: int = 16) -> dict[str, Any]:
    countries, catalog = _load_countries(); allowed=set(countries)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True); RAW_CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    chunk_records=[]; t0=time.monotonic()
    for idx, indicators in enumerate(_chunks(CANDIDATE_INDICATORS, CHUNK_SIZE), start=1):
        start=time.monotonic()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            by_indicator = {req["indicator_code"]: req for req in pool.map(lambda ind: fetch_one(ind, allowed, timeout_seconds), indicators)}
        requests=[by_indicator[i] for i in indicators]
        raw={"scope": base_scope(indicators, idx), "country_catalog": {"source_fixture": str(COUNTRY_CATALOG_FIXTURE.relative_to(PROJECT_ROOT)), "countries": catalog}, "requests": requests}
        raw_path=RAW_CHUNK_DIR / f"task-199-wdi-external-debt-raw-chunk-{idx:02d}.json"
        raw_path.write_text(json.dumps(raw, indent=2, sort_keys=True)+"\n", encoding='utf-8')
        resumed=sum(1 for r in requests if r.get('checkpoint_status')=='resumed_from_checkpoint')
        fetched=sum(1 for r in requests if r.get('checkpoint_status')=='fetched_and_checkpointed')
        rec={"chunk_index": idx, "indicator_count": len(indicators), "raw_path": str(raw_path.relative_to(PROJECT_ROOT)), "raw_sha256": _file_sha(raw_path), "resumed_from_checkpoint": resumed, "fetched_this_run": fetched, "elapsed_seconds": round(time.monotonic()-start,3)}
        chunk_records.append(rec)
    return {"scope": base_scope(CANDIDATE_INDICATORS, None) | {"chunk_count": len(chunk_records), "chunk_records": chunk_records, "elapsed_seconds": round(time.monotonic()-t0,3)}, "country_catalog": {"source_fixture": str(COUNTRY_CATALOG_FIXTURE.relative_to(PROJECT_ROOT)), "countries": catalog}, "requests": []}


def _parts(req: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    resp=req.get('response')
    if not isinstance(resp, list): raise ValueError('unsupported response structure: response is not a JSON list')
    if len(resp)==1 and isinstance(resp[0], dict) and 'message' in resp[0]: raise ValueError('provider_error_message')
    if len(resp)!=2 or not isinstance(resp[0], dict) or not isinstance(resp[1], list): raise ValueError('unsupported response structure: expected [metadata, observations]')
    return resp[0], resp[1]


def _metadata_known(req: dict[str, Any]) -> bool | None:
    meta=req.get('metadata_response')
    if isinstance(meta, list) and len(meta)==2 and isinstance(meta[1], list): return len(meta[1])>0
    if isinstance(meta, list) and len(meta)==1 and isinstance(meta[0], dict) and 'message' in meta[0]: return False
    return None


def _provider_message(req: dict[str, Any]) -> str | None:
    resp=req.get('response')
    if isinstance(resp, list) and len(resp)==1 and isinstance(resp[0], dict) and 'message' in resp[0]: return json.dumps(resp[0].get('message'), sort_keys=True)
    return None


def classify(raw: dict[str, Any], min_non_null_observations: int=1) -> dict[str, Any]:
    countries=list(raw['scope']['countries']); country_set=set(countries)
    results={}; included=[]; excluded=[]; arch=[]; outside=[]
    for req in raw['requests']:
        indicator=req['indicator_code']; ev={"indicator": indicator, "classification": "compatible", "provider_evidence_category": "compatible_annual_scalar_observations", "exclusion_evidence": None, "provider_label": None, "provider_lastupdated": None, "provider_total": None, "provider_total_before_non_aggregate_filter": None, "returned_row_count":0, "expected_max_rows": len(countries)*len(PERIODS), "countries_with_rows":0, "countries_with_observations":0, "periods": [], "period_count":0, "non_null_observation_count":0, "missing_observation_count":0, "non_null_density":0.0, "response_sha256": _sha256_blob(req.get('response')), "metadata_sha256": _sha256_blob(req.get('metadata_response')), "metadata_known_indicator": _metadata_known(req), "data_url": req.get('url'), "metadata_url": req.get('metadata_url')}
        try:
            meta, obs = _parts(req)
        except ValueError as exc:
            ev['classification']='provider_unavailable'; ev['provider_evidence_category']='provider_unavailable_invalid_indicator' if _metadata_known(req) is False else 'unsupported_response_structure'; ev['exclusion_evidence']=_provider_message(req) or str(exc)
            outside.append(indicator); excluded.append(indicator); results[indicator]=ev; continue
        ev['provider_lastupdated']=meta.get('lastupdated'); ev['provider_total']=meta.get('total'); ev['provider_total_before_non_aggregate_filter']=meta.get('total_before_non_aggregate_filter'); ev['returned_row_count']=len(obs)
        row_c=set(); val_c=set(); periods=set(); non_null=0; bad=None; wrong=None; out=set(); nonannual=set(); label=None
        for row in obs:
            ind=row.get('indicator') or {}; c=row.get('country') or {}; iso=row.get('countryiso3code'); per=str(row.get('date')); label=label or ind.get('value')
            if not ind.get('id') or not iso or not per or not c: bad='missing required WDI scalar observation fields'; break
            if ind.get('id') != indicator: wrong=ind.get('id'); break
            if iso not in country_set: out.add(str(iso))
            if not per.isdigit() or len(per)!=4: nonannual.add(per)
            periods.add(per); row_c.add(str(iso))
            if row.get('value') is not None: non_null += 1; val_c.add(str(iso))
        ev.update({"provider_label": label, "countries_with_rows": len(row_c), "countries_with_observations": len(val_c), "periods": sorted(periods), "period_count": len(periods), "non_null_observation_count": non_null, "missing_observation_count": len(obs)-non_null, "non_null_density": round(non_null/len(obs),6) if obs else 0.0})
        if bad:
            ev['classification']='incompatible_representation'; ev['provider_evidence_category']='unsupported_response_structure'; ev['exclusion_evidence']=bad; arch.append(indicator); excluded.append(indicator)
        elif wrong:
            ev['classification']='changed_provider_semantics'; ev['provider_evidence_category']='changed_provider_semantics'; ev['exclusion_evidence']=f'response contained unexpected indicator {wrong}'; outside.append(indicator); excluded.append(indicator)
        elif out:
            ev['classification']='incompatible_representation'; ev['provider_evidence_category']='outside_non_aggregate_country_scope'; ev['exclusion_evidence']=f'response contained countries outside non-aggregate scope: {sorted(out)[:10]}'; outside.append(indicator); excluded.append(indicator)
        elif nonannual:
            ev['classification']='incompatible_representation'; ev['provider_evidence_category']='non_annual_periods'; ev['exclusion_evidence']=f'response contained non-annual periods: {sorted(nonannual)[:10]}'; arch.append(indicator); excluded.append(indicator)
        elif len(obs)==0:
            ev['classification']='provider_unavailable'; ev['provider_evidence_category']='zero_observations_within_requested_scope'; ev['exclusion_evidence']='provider returned zero non-aggregate rows for requested countries/date range'; outside.append(indicator); excluded.append(indicator)
        elif non_null < min_non_null_observations:
            ev['classification']='provider_unavailable'; ev['provider_evidence_category']='zero_non_null_observations_within_requested_scope'; ev['exclusion_evidence']='provider returned rows but zero non-null observations'; outside.append(indicator); excluded.append(indicator)
        else: included.append(indicator)
        results[indicator]=ev
    return {"task": TASK_ID, "campaign": CAMPAIGN_NAME, "candidate_count": len(raw['scope']['indicators']), "included_indicators": sorted(included), "included_indicator_count": len(included), "excluded_indicators": sorted(set(excluded)), "excluded_indicator_count": len(set(excluded)), "requested_country_count": len(countries), "requested_date_range": DATE_RANGE, "requested_max_presparsity_rows": len(countries)*len(PERIODS)*len(raw['scope']['indicators']), "partition": {"immediately_ingestible": sorted(included), "requires_architectural_investigation": sorted(set(arch)), "provider_or_scope_exclusion": sorted(set(outside))}, "indicator_results": {k:results[k] for k in sorted(results)}}


def normalize(raw: dict[str, Any]) -> dict[str, Any]:
    classification=classify(raw); included=set(classification['included_indicators']); catalog={r['id']: r for r in raw['country_catalog']['countries']}; countries=list(raw['scope']['countries'])
    rows=[]; raw_artifacts=[]; evidence_manifest=[]
    for req in raw['requests']:
        indicator=req['indicator_code']; ev=classification['indicator_results'][indicator]; response_bytes=len(json.dumps(req.get('response'), sort_keys=True).encode())
        manifest={"indicator": indicator, "url": req.get('url'), "metadata_url": req.get('metadata_url'), "sha256": _sha256_blob(req.get('response')), "response_sha256": _sha256_blob(req.get('response')), "metadata_sha256": _sha256_blob(req.get('metadata_response')), "bytes": response_bytes, "classification": ev['classification'], "provider_evidence_category": ev['provider_evidence_category'], "preservation_status": "preserved_in_per_indicator_checkpoint_and_raw_chunk"}
        evidence_manifest.append(manifest)
        if indicator not in included: continue
        meta, obs = _parts(req); raw_artifacts.append({**manifest, "status": "ok", "content_type": "application/json", "row_count": len(obs), "non_null_observation_count": ev['non_null_observation_count'], "source_metadata": meta})
        for item in obs:
            ind=item.get('indicator') or {}; country=item.get('country') or {}; iso=item.get('countryiso3code'); cat=catalog.get(iso,{})
            rows.append({"source": SOURCE_NAME, "indicator_id": ind.get('id'), "indicator_name": ind.get('value'), "country_id": country.get('id'), "country_name": (cat.get('name') or cat.get('value') or country.get('value')), "countryiso3code": iso, "date": str(item.get('date')), "value": item.get('value'), "unit": item.get('unit') or None, "obs_status": item.get('obs_status') or None, "decimal": item.get('decimal'), "repository_section": "external_debt_large_chunked", "operational_capability": "External debt stocks, flows, debt service, creditor composition, concessionality, arrears, and reserve/debt vulnerability monitoring", "operational_mode": CAMPAIGN_MODE, "coverage_level": "implemented_compatible_wdi_economy_growth_chunked_annual_scalar_campaign", "region_id": (cat.get('region') or {}).get('id'), "region_label": (cat.get('region') or {}).get('value'), "income_level_id": (cat.get('incomeLevel') or {}).get('id'), "income_level_label": (cat.get('incomeLevel') or {}).get('value')})
    c_order={c:i for i,c in enumerate(countries)}; i_order={ind:i for i,ind in enumerate(classification['included_indicators'])}
    rows.sort(key=lambda r: (i_order[r['indicator_id']], c_order.get(r['countryiso3code'],9999), int(r['date'])))
    observed=sum(1 for r in rows if r['value'] is not None)
    raw_artifact_path = raw['scope'].get('raw_chunk_path') or raw['scope'].get('raw_manifest_path') or str(BASE_RAW_DIR.relative_to(PROJECT_ROOT))
    normalized_artifact_path = raw['scope'].get('normalized_chunk_path') or str(NORM_CHUNK_DIR.relative_to(PROJECT_ROOT))
    normalized={"task": TASK_ID, "campaign": CAMPAIGN_NAME, "mode": CAMPAIGN_MODE, "source": SOURCE_NAME, "support_bundle": raw_artifact_path, "raw_evidence_preservation": {"policy": raw['scope']['raw_evidence_policy'], "raw_artifact": raw_artifact_path, "normalized_artifact": normalized_artifact_path, "raw_artifact_sha256": _sha256_blob(raw), "deletion_performed": False, "cleanup_proposed": False}, "countries": countries, "country_count": len(countries), "indicators": classification['included_indicators'], "indicator_count": classification['included_indicator_count'], "excluded_indicators": classification['excluded_indicators'], "date_range": DATE_RANGE, "expected_row_count": len(rows), "row_count": len(rows), "observed_value_count": observed, "missing_value_count": len(rows)-observed, "rows": rows, "raw_artifacts": raw_artifacts, "evidence_manifest": evidence_manifest, "classification": classification, "operational_scope": raw['scope']}
    normalized['normalized_artifact_sha256']=_sha256_blob({k:v for k,v in normalized.items() if k!='normalized_artifact_sha256'})
    return normalized


def write_artifacts(raw_all: dict[str, Any]) -> dict[str, Any]:
    BASE_RAW_DIR.mkdir(parents=True, exist_ok=True); BASE_PROCESSED_DIR.mkdir(parents=True, exist_ok=True); RAW_CHUNK_DIR.mkdir(parents=True, exist_ok=True); NORM_CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    chunk_man=[]; all_class={}; total_rows=0; total_obs=0; total_missing=0; included=[]; excluded=[]
    requests_by={r['indicator_code']: r for r in raw_all.get('requests', [])}
    _, catalog = _load_countries()
    for idx, indicators in enumerate(_chunks(CANDIDATE_INDICATORS, CHUNK_SIZE), start=1):
        raw_path=RAW_CHUNK_DIR / f"task-199-wdi-external-debt-raw-chunk-{idx:02d}.json"
        if raw_path.exists(): raw=_read_json(raw_path)
        else:
            raw={"scope": base_scope(indicators, idx), "country_catalog": {"source_fixture": str(COUNTRY_CATALOG_FIXTURE.relative_to(PROJECT_ROOT)), "countries": catalog}, "requests": [requests_by[i] for i in indicators]}
        raw['scope']['raw_chunk_path']=str(raw_path.relative_to(PROJECT_ROOT))
        norm_path=NORM_CHUNK_DIR / f"task-199-wdi-external-debt-normalized-chunk-{idx:02d}.json"
        raw['scope']['normalized_chunk_path']=str(norm_path.relative_to(PROJECT_ROOT))
        raw_path.write_text(json.dumps(raw, indent=2, sort_keys=True)+"\n", encoding='utf-8')
        norm=normalize(raw)
        norm_path.write_text(json.dumps(norm, indent=2, sort_keys=True)+"\n", encoding='utf-8')
        all_class.update(norm['classification']['indicator_results']); total_rows += norm['row_count']; total_obs += norm['observed_value_count']; total_missing += norm['missing_value_count']; included.extend(norm['indicators']); excluded.extend(norm['excluded_indicators'])
        chunk_man.append({"chunk_index": idx, "candidate_count": len(indicators), "included_indicator_count": norm['indicator_count'], "excluded_indicator_count": len(norm['excluded_indicators']), "row_count": norm['row_count'], "observed_value_count": norm['observed_value_count'], "raw_path": str(raw_path.relative_to(PROJECT_ROOT)), "raw_sha256": _file_sha(raw_path), "normalized_path": str(norm_path.relative_to(PROJECT_ROOT)), "normalized_sha256": _file_sha(norm_path)})
    manifest={"task": TASK_ID, "campaign": CAMPAIGN_NAME, "mode": CAMPAIGN_MODE, "candidate_count": len(CANDIDATE_INDICATORS), "chunk_size": CHUNK_SIZE, "chunk_count": len(chunk_man), "included_indicators": sorted(set(included)), "included_indicator_count": len(set(included)), "excluded_indicators": sorted(set(excluded)), "excluded_indicator_count": len(set(excluded)), "row_count": total_rows, "observed_value_count": total_obs, "missing_value_count": total_missing, "country_count": len(raw_all['scope']['countries']), "date_range": DATE_RANGE, "chunks": chunk_man, "classification": {"indicator_results": {k: all_class[k] for k in sorted(all_class)}}, "execution_improvements": raw_all['scope']['execution_improvements'], "operational_scope": raw_all['scope']}
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n", encoding='utf-8')
    return manifest


def main(argv: list[str] | None=None) -> int:
    p=argparse.ArgumentParser()
    p.add_argument('command', choices=['fetch','manifest'])
    p.add_argument('--timeout-seconds', type=int, default=45)
    p.add_argument('--max-workers', type=int, default=16)
    args=p.parse_args(argv)
    if args.command=='fetch':
        raw=fetch_raw(args.timeout_seconds, args.max_workers)
        manifest=write_artifacts(raw)
        print(json.dumps({"status":"complete", "candidate_count": manifest['candidate_count'], "chunk_count": manifest['chunk_count'], "included_indicator_count": manifest['included_indicator_count'], "excluded_indicator_count": manifest['excluded_indicator_count'], "row_count": manifest['row_count'], "elapsed_seconds": raw['scope'].get('elapsed_seconds')}, sort_keys=True))
    elif args.command=='manifest':
        raw={"scope": base_scope(CANDIDATE_INDICATORS, None), "country_catalog": {"source_fixture": str(COUNTRY_CATALOG_FIXTURE.relative_to(PROJECT_ROOT)), "countries": _load_countries()[1]}, "requests": [_read_json(_checkpoint_path(i)) for i in CANDIDATE_INDICATORS]}
        manifest=write_artifacts(raw); print(json.dumps({"status":"complete", "row_count": manifest['row_count']}, sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
