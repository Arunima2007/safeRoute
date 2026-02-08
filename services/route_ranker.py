# services/route_ranker.py - FIXED WITH DEBUGGING

class RouteRanker:
    
    def rank_routes(self, routes_with_scores, preference):
        """
        Rank routes based on user preference
        """
        
        if not routes_with_scores:
            return []
        
        # CRITICAL FIX: Make preference case-insensitive and handle None
        preference = str(preference).lower().strip() if preference else 'balanced'
        
        print(f"\n{'='*60}")
        print(f"🎯 RANKING with preference: '{preference}'")
        print(f"{'='*60}")
        
        # Calculate speed scores - IMPROVED LOGIC
        durations = [r['duration_seconds'] for r in routes_with_scores]
        min_duration = min(durations)
        max_duration = max(durations)
        duration_range = max_duration - min_duration
        
        for route in routes_with_scores:
            if duration_range > 0:
                # Normalize to 0-1 range (0 = fastest, 1 = slowest)
                normalized = (route['duration_seconds'] - min_duration) / duration_range
                
                # Map to 60-100 range: fastest=100, slowest=60
                route['speed_score'] = 100 - (normalized * 20)
            else:
                # All routes same duration
                route['speed_score'] = 100.0
            
            print(f"  Route {route['summary']}: Speed={route['speed_score']:.1f}")
        
        # Define weights
        weights = {
            'safety': {'safety': 0.7, 'speed': 0.15, 'eco': 0.15},
            'fastest': {'safety': 0.15, 'speed': 0.7, 'eco': 0.15},
            'eco': {'safety': 0.15, 'speed': 0.15, 'eco': 0.7},
            'balanced': {'safety': 0.4, 'speed': 0.3, 'eco': 0.3}
        }
        
        # Get weights with fallback
        w = weights.get(preference, weights['balanced'])
        
        print(f"\n  Weights: Safety={w['safety']:.0%}, Speed={w['speed']:.0%}, Eco={w['eco']:.0%}")
        
        # Calculate composite scores WITH DETAILED DEBUG
        print(f"\n  Composite Score Calculation:")
        for route in routes_with_scores:
            safety = route['safety_score']
            speed = route['speed_score']
            eco = route['eco_score']
            
            composite = (safety * w['safety'] + 
                        speed * w['speed'] + 
                        eco * w['eco'])
            
            route['composite_score'] = composite
            
            print(f"    {route['summary'][:30]}...")
            print(f"      {safety:.1f}×{w['safety']:.2f} + {speed:.1f}×{w['speed']:.2f} + {eco:.1f}×{w['eco']:.2f}")
            print(f"      = {safety*w['safety']:.2f} + {speed*w['speed']:.2f} + {eco*w['eco']:.2f}")
            print(f"      = {composite:.2f}")
        
        # Sort by composite score (HIGHEST first)
        ranked_routes = sorted(
            routes_with_scores, 
            key=lambda x: x['composite_score'], 
            reverse=True  # CRITICAL: reverse=True means highest score wins
        )
        
        print(f"\n  Final Ranking:")
        for idx, route in enumerate(ranked_routes):
            print(f"    #{idx+1}: {route['summary']} (Score: {route['composite_score']:.1f})")
        print(f"{'='*60}\n")
        
        # Add rank and explanations
        for idx, route in enumerate(ranked_routes):
            route['rank'] = idx + 1
            route['explanation'] = self._generate_explanation(
                route, preference, idx == 0
            )
        
        return ranked_routes
    
    def _generate_explanation(self, route, preference, is_best):
        """Generate detailed explanation based on preference"""
        
        # Get actual values for better descriptions
        crime = route.get('avg_crime', 0.5)
        lighting = route.get('avg_lighting', 0.5)
        pollution = route.get('avg_pollution', 0.5)
        carbon = route.get('avg_carbon', 0.5)
        traffic = route.get('avg_traffic', 0.5)
        
        if preference == 'safety':
            # Safety-focused explanation
            parts = []
            
            # Crime assessment
            if crime < 0.25:
                parts.append("✅ Very safe area with minimal crime")
            elif crime < 0.35:
                parts.append("✅ Low crime neighborhood")
            elif crime < 0.50:
                parts.append("⚠️ Moderate crime area - stay alert")
            else:
                parts.append("🚨 Higher crime area - extra caution advised")
            
            # Lighting assessment
            if lighting > 0.75:
                parts.append("with excellent street lighting")
            elif lighting > 0.60:
                parts.append("with good lighting infrastructure")
            elif lighting > 0.45:
                parts.append("with adequate lighting (use caution at night)")
            else:
                parts.append("with poor lighting - avoid after dark")
            
            explanation = ". ".join(parts) + f". Overall safety: {route['safety_score']:.0f}/100."
        
        elif preference == 'fastest':
            # Speed-focused explanation
            speed_rating = "⚡ Fastest option" if route['speed_score'] > 90 else \
                          "🏃 Quick route" if route['speed_score'] > 70 else \
                          "🐌 Slower option"
            
            traffic_desc = "light traffic" if traffic < 0.4 else \
                          "moderate traffic" if traffic < 0.7 else \
                          "heavy congestion"
            
            explanation = f"{speed_rating}: {route['duration_text']} with {traffic_desc}. Speed score: {route['speed_score']:.0f}/100."
        
        elif preference == 'eco':
            # Eco-focused explanation
            if route['eco_score'] > 70:
                eco_rating = "🌟 Most eco-friendly option"
            elif route['eco_score'] > 60:
                eco_rating = "🌿 Good environmental choice"
            else:
                eco_rating = "🏭 Higher environmental impact"
            
            # Air quality
            if pollution < 0.35:
                air_quality = "excellent air quality"
            elif pollution < 0.50:
                air_quality = "moderate air quality"
            else:
                air_quality = "poor air quality"
            
            # Carbon emissions
            co2_estimate = (route.get('distance_meters', 0) / 1000) * 0.12 * carbon  # kg CO2
            
            explanation = f"{eco_rating}: {air_quality}, ~{co2_estimate:.2f}kg CO₂ emissions. Eco score: {route['eco_score']:.0f}/100."
        
        else:  # balanced
            explanation = (
                f"⚖️ Balanced route scoring {route['composite_score']:.0f}/100. "
                f"Safety: {route['safety_score']:.0f}, Speed: {route['speed_score']:.0f}, Eco: {route['eco_score']:.0f}. "
                f"{self._get_balanced_summary(route)}"
            )
        
        if is_best:
            return f"⭐ RECOMMENDED: {explanation}"
        
        return explanation
    
    def _get_balanced_summary(self, route):
        """Get summary for balanced mode"""
        strengths = []
        weaknesses = []
        
        if route['safety_score'] > 65:
            strengths.append("safe")
        elif route['safety_score'] < 50:
            weaknesses.append("safety concerns")
        
        if route['speed_score'] > 65:
            strengths.append("fast")
        elif route['speed_score'] < 50:
            weaknesses.append("slower")
        
        if route['eco_score'] > 65:
            strengths.append("eco-friendly")
        elif route['eco_score'] < 50:
            weaknesses.append("higher emissions")
        
        parts = []
        if strengths:
            parts.append(f"Strong on: {', '.join(strengths)}")
        if weaknesses:
            parts.append(f"Watch out: {', '.join(weaknesses)}")
        
        return ". ".join(parts) if parts else "Good all-around choice"