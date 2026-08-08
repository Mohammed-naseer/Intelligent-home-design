"""
Requirement Analyzer Module - AI House Architect
Parses, validates, and normalizes user input requirements into a structured design specification.
Does not rely on external LLM APIs; uses deterministic schema parsing and architectural rules.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class PlotSpec(BaseModel):
    length: float = Field(..., gt=0, description="Plot length in feet")
    width: float = Field(..., gt=0, description="Plot width in feet")

    @property
    def area_sqft(self) -> float:
        return self.length * self.width


class RoomRequirements(BaseModel):
    bedrooms: int = Field(default=3, ge=1, le=10)
    bathrooms: int = Field(default=2, ge=1, le=10)
    kitchen: int = Field(default=1, ge=1, le=3)
    living_dining: int = Field(default=1, ge=1, le=3)
    parking: int = Field(default=1, ge=0, le=5)
    balcony: int = Field(default=1, ge=0, le=5)
    garden: bool = Field(default=True)
    home_office: bool = Field(default=False)
    pooja_prayer_room: bool = Field(default=False)


class DesignRequirement(BaseModel):
    plot: PlotSpec
    floors: int = Field(default=1, ge=1, le=4)
    rooms: RoomRequirements
    budget: str = Field(default="standard", description="economy, standard, premium, luxury")
    architectural_style: str = Field(default="modern", description="modern, traditional, contemporary, minimalist, colonial")
    climate_location: str = Field(default="tropical", description="tropical, temperate, arid, cold, coastal")
    cultural_preference: str = Field(default="none", description="none, vastu, feng_shui, qibla, contemporary")
    accessibility: bool = Field(default=False, description="Wheelchair accessible ground floor & wider corridors")
    future_expansion: bool = Field(default=False, description="Design for future top floor addition")


class RequirementAnalyzer:
    """Deterministic analyzer and normalizer for architectural requirements."""

    def __init__(self):
        self.default_styles = ["modern", "traditional", "contemporary", "minimalist", "colonial"]
        self.default_cultural = ["none", "vastu", "feng_shui", "qibla", "contemporary"]
        self.default_budgets = ["economy", "standard", "premium", "luxury"]

    def analyze(self, raw_input: Dict[str, Any]) -> DesignRequirement:
        """Parses and validates raw input into normalized DesignRequirement."""
        plot_data = raw_input.get("plot", {})
        length = float(plot_data.get("length", raw_input.get("plot_length", 50.0)))
        width = float(plot_data.get("width", raw_input.get("plot_width", 40.0)))

        rooms_data = raw_input.get("rooms", {})
        bedrooms = int(rooms_data.get("bedrooms", raw_input.get("bedrooms", 3)))
        bathrooms = int(rooms_data.get("bathrooms", raw_input.get("bathrooms", 2)))
        kitchen = int(rooms_data.get("kitchen", raw_input.get("kitchen", 1)))
        living_dining = int(rooms_data.get("living_dining", raw_input.get("living_dining", 1)))
        parking = int(rooms_data.get("parking", raw_input.get("parking", 1)))
        balcony = int(rooms_data.get("balcony", raw_input.get("balcony", 1)))
        garden = bool(rooms_data.get("garden", raw_input.get("garden", True)))
        home_office = bool(rooms_data.get("home_office", raw_input.get("home_office", False)))
        pooja_prayer = bool(rooms_data.get("pooja_prayer_room", raw_input.get("pooja_prayer_room", False)))

        floors = int(raw_input.get("floors", 2 if bedrooms > 3 else 1))
        budget = str(raw_input.get("budget", "standard")).lower()
        if budget not in self.default_budgets:
            budget = "standard"

        style = str(raw_input.get("architectural_style", raw_input.get("style", "modern"))).lower()
        if style not in self.default_styles:
            style = "modern"

        cultural = str(raw_input.get("cultural_preference", raw_input.get("cultural", "none"))).lower()
        if cultural not in self.default_cultural:
            cultural = "none"

        climate = str(raw_input.get("climate_location", raw_input.get("climate", "tropical"))).lower()
        accessibility = bool(raw_input.get("accessibility", False))
        future_expansion = bool(raw_input.get("future_expansion", False))

        room_reqs = RoomRequirements(
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            kitchen=kitchen,
            living_dining=living_dining,
            parking=parking,
            balcony=balcony,
            garden=garden,
            home_office=home_office,
            pooja_prayer_room=pooja_prayer,
        )

        return DesignRequirement(
            plot=PlotSpec(length=length, width=width),
            floors=floors,
            rooms=room_reqs,
            budget=budget,
            architectural_style=style,
            climate_location=climate,
            cultural_preference=cultural,
            accessibility=accessibility,
            future_expansion=future_expansion,
        )


requirement_analyzer = RequirementAnalyzer()
