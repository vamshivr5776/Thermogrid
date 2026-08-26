from thermal.analysis_service import ThermoGridAnalysisService


def test_analysis_service_import():
    service = ThermoGridAnalysisService()

    assert service.pipeline is not None
    assert service.thermal_model is not None
    assert service.risk_engine is not None