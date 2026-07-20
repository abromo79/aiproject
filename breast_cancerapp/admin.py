from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import RiskAssessment, ImageAnalysis

@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = (
        'created_at', 'age', 'prediction_with_badge', 'confidence_with_bar', 
        'medical_history', 'genetic_factors', 'risk_level'
    )
    list_filter = (
        'prediction', 'history_breast_cancer_or_radiation', 
        'brca_mutation_or_genetic_syndrome', 'created_at'
    )
    search_fields = (
        'sub_ethnicity_or_birthplace', 'age', 'prediction'
    )
    readonly_fields = ('created_at', 'confidence_percent')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('age', 'sub_ethnicity_or_birthplace'),
            'description': 'Basic demographic information for risk assessment'
        }),
        ('Medical History', {
            'fields': (
                'history_breast_cancer_or_radiation', 
                'brca_mutation_or_genetic_syndrome',
                'first_degree_relative_with_breast_cancer',
                'over_55_years_old_at_first_live_birth',
                'no_pregnancy_or_over_30_years_old_at_first_live_birth',
                'menstrual_cycle_irregularities_or_short_menstrual_cycle',
                'ever_used_oral_contraceptives',
                'ever_used_hormone_replacement_therapy',
                'ever_had_breast_biopsy',
                'high_breast_density_on_mammogram'
            ),
            'description': 'Medical and reproductive history factors'
        }),
        ('AI Analysis Results', {
            'fields': ('prediction', 'confidence_percent'),
            'description': 'Machine learning model predictions and confidence scores'
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',),
            'description': 'Timestamp information'
        })
    )
    
    def prediction_with_badge(self, obj):
        if obj.prediction.lower() in ['high', 'positive']:
            return format_html(
                '<span style="background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; padding: 6px 14px; border-radius: 25px; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3); border: 2px solid rgba(255, 255, 255, 0.2);">{}</span>',
                obj.prediction
            )
        elif obj.prediction.lower() in ['low', 'negative', 'benign']:
            return format_html(
                '<span style="background: linear-gradient(135deg, #059669, #047857); color: white; padding: 6px 14px; border-radius: 25px; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 4px 15px rgba(5, 150, 105, 0.3); border: 2px solid rgba(255, 255, 255, 0.2);">{}</span>',
                obj.prediction
            )
        else:
            return format_html(
                '<span style="background: linear-gradient(135deg, #d97706, #b45309); color: white; padding: 6px 14px; border-radius: 25px; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 4px 15px rgba(217, 119, 6, 0.3); border: 2px solid rgba(255, 255, 255, 0.2);">{}</span>',
                obj.prediction
            )
    prediction_with_badge.short_description = 'Risk Level'
    prediction_with_badge.admin_order_field = 'prediction'
    
    def confidence_with_bar(self, obj):
        confidence = obj.confidence_percent or 0
        if confidence >= 80:
            color = '#059669'
            bg_color = '#d1fae5'
            text_color = '#065f46'
        elif confidence >= 60:
            color = '#d97706'
            bg_color = '#fed7aa'
            text_color = '#92400e'
        else:
            color = '#dc2626'
            bg_color = '#fecaca'
            text_color = '#991b1b'
            
        return format_html(
            '<div style="display: flex; align-items: center; gap: 12px;">'
            '<div style="flex: 1; height: 24px; background: {}; border-radius: 12px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);">'
            '<div style="width: {}%; height: 100%; background: linear-gradient(135deg, {}, {}); transition: all 0.5s ease; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);"></div>'
            '</div>'
            '<span style="font-weight: 700; color: {}; font-size: 14px; background: {}; padding: 4px 8px; border-radius: 8px;">{}%</span>'
            '</div>',
            bg_color, confidence, color, color + 'dd', text_color, bg_color, confidence
        )
    confidence_with_bar.short_description = 'Confidence'
    confidence_with_bar.admin_order_field = 'confidence_percent'
    
    def medical_history(self, obj):
        history_items = []
        if obj.history_breast_cancer_or_radiation:
            history_items.append('Cancer/Radiation')
        if obj.first_degree_relative_with_breast_cancer:
            history_items.append('Family History')
        if obj.over_55_years_old_at_first_live_birth:
            history_items.append('Late First Birth')
        
        if history_items:
            return format_html(
                '<span style="color: #6b7280;">{}</span>',
                ', '.join(history_items[:2]) + ('...' if len(history_items) > 2 else '')
            )
        return format_html('<span style="color: #9ca3af; font-style: italic;">None</span>')
    medical_history.short_description = 'Medical History'
    
    def genetic_factors(self, obj):
        factors = []
        if obj.brca_mutation_or_genetic_syndrome:
            factors.append('BRCA')
        if obj.high_breast_density_on_mammogram:
            factors.append('High Density')
        
        if factors:
            return format_html(
                '<span style="color: #6b7280;">{}</span>',
                ', '.join(factors)
            )
        return format_html('<span style="color: #9ca3af; font-style: italic;">None</span>')
    genetic_factors.short_description = 'Genetic Factors'
    
    def risk_level(self, obj):
        if obj.prediction.lower() in ['high', 'positive']:
            return format_html(
                '<span style="color: #dc2626; font-weight: 700;">HIGH RISK</span>'
            )
        elif obj.prediction.lower() in ['low', 'negative', 'benign']:
            return format_html(
                '<span style="color: #059669; font-weight: 700;">LOW RISK</span>'
            )
        else:
            return format_html(
                '<span style="color: #d97706; font-weight: 700;">MODERATE</span>'
            )
    risk_level.short_description = 'Risk Assessment'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related().prefetch_related()
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(ImageAnalysis)
class ImageAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        'created_at', 'image_preview', 'prediction_with_badge', 
        'confidence_with_bar', 'stage_with_color', 'analysis_status'
    )
    list_filter = (
        'prediction', 'stage', 'created_at'
    )
    search_fields = (
        'image_name', 'prediction_label', 'stage'
    )
    readonly_fields = (
        'created_at', 'confidence_percent', 
        'image_preview', 'prediction_label', 'stage'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Image Information', {
            'fields': ('image', 'image_name', 'image_preview'),
            'description': 'Medical image for breast cancer analysis'
        }),
        ('AI Analysis Results', {
            'fields': (
                'prediction', 'prediction_label', 'confidence_percent', 
                'stage', 'prediction_values'
            ),
            'description': 'Deep learning model analysis results'
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',),
            'description': 'Timestamp and system information'
        })
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px; border: 2px solid #e5e7eb;" />',
                obj.image.url
            )
        return format_html(
            '<span style="color: #9ca3af; font-style: italic;">No image</span>'
        )
    image_preview.short_description = 'Image'
    
    def prediction_with_badge(self, obj):
        prediction = obj.prediction_label or obj.prediction or 'Unknown'
        if prediction.lower() in ['malignant', 'positive', 'cancer']:
            return format_html(
                '<span style="background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; padding: 6px 14px; border-radius: 25px; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3); border: 2px solid rgba(255, 255, 255, 0.2);">{}</span>',
                prediction
            )
        elif prediction.lower() in ['benign', 'negative', 'normal']:
            return format_html(
                '<span style="background: linear-gradient(135deg, #059669, #047857); color: white; padding: 6px 14px; border-radius: 25px; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 4px 15px rgba(5, 150, 105, 0.3); border: 2px solid rgba(255, 255, 255, 0.2);">{}</span>',
                prediction
            )
        else:
            return format_html(
                '<span style="background: linear-gradient(135deg, #d97706, #b45309); color: white; padding: 6px 14px; border-radius: 25px; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 4px 15px rgba(217, 119, 6, 0.3); border: 2px solid rgba(255, 255, 255, 0.2);">{}</span>',
                prediction
            )
    prediction_with_badge.short_description = 'Prediction'
    prediction_with_badge.admin_order_field = 'prediction'
    
    def confidence_with_bar(self, obj):
        confidence = obj.confidence_percent or 0
        if confidence >= 80:
            color = '#059669'
            bg_color = '#d1fae5'
            text_color = '#065f46'
        elif confidence >= 60:
            color = '#d97706'
            bg_color = '#fed7aa'
            text_color = '#92400e'
        else:
            color = '#dc2626'
            bg_color = '#fecaca'
            text_color = '#991b1b'
            
        return format_html(
            '<div style="display: flex; align-items: center; gap: 12px;">'
            '<div style="flex: 1; height: 24px; background: {}; border-radius: 12px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);">'
            '<div style="width: {}%; height: 100%; background: linear-gradient(135deg, {}, {}); transition: all 0.5s ease; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);"></div>'
            '</div>'
            '<span style="font-weight: 700; color: {}; font-size: 14px; background: {}; padding: 4px 8px; border-radius: 8px;">{}%</span>'
            '</div>',
            bg_color, confidence, color, color + 'dd', text_color, bg_color, confidence
        )
    confidence_with_bar.short_description = 'Confidence'
    confidence_with_bar.admin_order_field = 'confidence_percent'
    
    def stage_with_color(self, obj):
        if not obj.stage:
            return format_html('<span style="color: #9ca3af; font-style: italic; font-weight: 600;">N/A</span>')
        
        stage_colors = {
            '0': ('#059669', '#047857'),      # Green - Normal
            'I': ('#2563eb', '#1d4ed8'),      # Blue - Early
            'II': ('#d97706', '#b45309'),     # Orange - Moderate
            'III': ('#dc2626', '#b91c1c'),    # Red - Advanced
            'IV': ('#7c3aed', '#6d28d9'),     # Purple - Late
        }
        
        colors = stage_colors.get(obj.stage, ('#6b7280', '#4b5563'))
        return format_html(
            '<span style="background: linear-gradient(135deg, {}, {}); color: white; padding: 6px 12px; border-radius: 20px; font-weight: 700; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); border: 2px solid rgba(255, 255, 255, 0.2);">Stage {}</span>',
            colors[0], colors[1], obj.stage
        )
    stage_with_color.short_description = 'Cancer Stage'
    stage_with_color.admin_order_field = 'stage'
    
    def analysis_status(self, obj):
        confidence = obj.confidence_percent or 0
        if confidence >= 80:
            return format_html(
                '<span style="color: #059669; font-weight: 700;">HIGH CONFIDENCE</span>'
            )
        elif confidence >= 60:
            return format_html(
                '<span style="color: #d97706; font-weight: 700;">MODERATE</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc2626; font-weight: 700;">LOW CONFIDENCE</span>'
            )
    analysis_status.short_description = 'Analysis Quality'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related().prefetch_related()
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


# Customize admin site header and title
admin.site.site_header = 'Breast Cancer AI Administration'
admin.site.site_title = 'Breast Cancer AI Admin'
admin.site.index_title = 'Medical AI System Dashboard'

# Add custom admin site styling
class BreastCancerAdminSite(admin.AdminSite):
    site_header = 'Breast Cancer AI Administration'
    site_title = 'Breast Cancer AI Admin'
    index_title = 'Medical AI System Dashboard'
    
    def each_context(self, request):
        context = super().each_context(request)
        context['site_header'] = 'Breast Cancer AI Administration'
        context['site_title'] = 'Breast Cancer AI Admin'
        context['index_title'] = 'Medical AI System Dashboard'
        return context
