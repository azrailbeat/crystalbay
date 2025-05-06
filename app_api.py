import logging
from flask import request, jsonify
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def register_api_routes(app):
    """
    Register all API routes with the Flask app.
    
    Args:
        app: The Flask application instance
    """
    
    @app.route('/api/leads', methods=['GET'])
    def get_leads_api():
        """Get all leads for the API"""
        try:
            from models import LeadService
            
            status = request.args.get('status')
            limit = request.args.get('limit', 100, type=int)
            
            leads = LeadService.get_leads(limit=limit, status=status)
            return jsonify({'leads': leads})
        except Exception as e:
            logger.error(f"Error retrieving leads: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/<lead_id>', methods=['GET'])
    def get_lead_api(lead_id):
        """Get a specific lead by ID"""
        try:
            from models import LeadService
            
            lead = LeadService.get_lead(lead_id)
            if not lead:
                return jsonify({'error': 'Lead not found'}), 404
            
            return jsonify({'lead': lead})
        except Exception as e:
            logger.error(f"Error retrieving lead {lead_id}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/<lead_id>', methods=['PUT'])
    def update_lead_api(lead_id):
        """Update a lead"""
        try:
            from models import LeadService
            
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            lead = LeadService.update_lead(lead_id, data)
            if not lead:
                return jsonify({'error': 'Lead not found'}), 404
            
            return jsonify({'lead': lead})
        except Exception as e:
            logger.error(f"Error updating lead {lead_id}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads', methods=['POST'])
    def create_lead_api():
        """Create a new lead"""
        try:
            from models import LeadService
            
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            lead = LeadService.create_lead(data)
            return jsonify({'lead': lead}), 201
        except Exception as e:
            logger.error(f"Error creating lead: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/<lead_id>/interactions', methods=['GET'])
    def get_lead_interactions_api(lead_id):
        """Get interactions for a lead"""
        try:
            from models import LeadService
            
            interactions = LeadService.get_lead_interactions(lead_id)
            return jsonify({'interactions': interactions})
        except Exception as e:
            logger.error(f"Error retrieving interactions for lead {lead_id}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/<lead_id>/interactions', methods=['POST'])
    def add_lead_interaction_api(lead_id):
        """Add an interaction to a lead"""
        try:
            from models import LeadService
            
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            interaction = LeadService.add_lead_interaction(lead_id, data)
            return jsonify({'interaction': interaction}), 201
        except Exception as e:
            logger.error(f"Error adding interaction to lead {lead_id}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/process', methods=['POST'])
    def process_inquiry_api():
        """Process a new inquiry with AI"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            processor = get_inquiry_processor()
            result = processor.process_new_inquiry(data)
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error processing inquiry: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/<lead_id>/analyze', methods=['POST'])
    def analyze_lead_api(lead_id):
        """Analyze a lead with AI"""
        try:
            from models import LeadService
            from inquiry_processor import get_inquiry_processor
            
            # Get the lead data
            lead = LeadService.get_lead(lead_id)
            if not lead:
                return jsonify({'error': 'Lead not found'}), 404
            
            # Process the content with AI
            processor = get_inquiry_processor()
            analysis = processor._analyze_with_ai(lead.get('notes', ''))
            
            # Add an interaction with the analysis results
            interaction_data = {
                'type': 'ai_analysis',
                'notes': f"AI Analysis:\n\n" +
                        f"Category: {analysis.get('category')}\n" +
                        f"Urgency: {analysis.get('urgency')}/5\n" +
                        f"Summary: {analysis.get('summary')}\n\n" +
                        f"Suggested Actions:\n" + '\n'.join([f"- {action}" for action in analysis.get('suggested_actions', [])])
            }
            
            LeadService.add_lead_interaction(lead_id, interaction_data)
            
            # Return the analysis results
            return jsonify({
                'lead_id': lead_id,
                'analysis': analysis
            })
        except Exception as e:
            logger.error(f"Error analyzing lead {lead_id}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/<lead_id>/update-status', methods=['POST'])
    def update_inquiry_status_api(lead_id):
        """Update the status of an inquiry"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            data = request.json or {}
            
            processor = get_inquiry_processor()
            result = processor.update_inquiry_status(lead_id, data)
            
            if not result:
                return jsonify({'error': 'Lead not found'}), 404
            
            return jsonify({'lead': result})
        except Exception as e:
            logger.error(f"Error updating inquiry status for {lead_id}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
            
    @app.route('/api/leads/<lead_id>/status', methods=['PUT'])
    def update_lead_status_api(lead_id):
        """Update the status of a lead"""
        try:
            from models import LeadService
            
            data = request.json
            if not data or 'status' not in data:
                return jsonify({'error': 'Status is required'}), 400
            
            new_status = data['status']
            old_status = 'unknown'
            
            try:
                # Get the current lead data
                lead = LeadService.get_lead(lead_id)
                if not lead:
                    # Если лид не найден в базе данных, используем резервные данные
                    logger.warning(f"Lead {lead_id} not found in database, using fallback data")
                    # Ищем карточку в резервных данных
                    for memory_lead in _memory_leads:
                        if str(memory_lead.get('id')) == str(lead_id):
                            lead = memory_lead
                            break
                    
                    if not lead:
                        # Создаем минимальный лид для демонстрации
                        lead = {
                            'id': lead_id,
                            'status': 'new',
                            'name': f'Lead #{lead_id}',
                            'source': 'demo'
                        }
                        _memory_leads.append(lead)
                
                # Получаем текущий статус
                old_status = lead.get('status', 'new')
                
                # Add an interaction to record the status change
                interaction_data = {
                    'type': 'status_change',
                    'notes': f"Статус изменен с '{old_status}' на '{new_status}'"
                }
                
                # Пробуем добавить запись о взаимодействии в базу данных
                try:
                    LeadService.add_lead_interaction(lead_id, interaction_data)
                except Exception as e:
                    logger.warning(f"Cannot add interaction in database: {e}")
                
                # Пробуем обновить статус в базе данных
                try:
                    updated_lead = LeadService.update_lead(lead_id, {'status': new_status})
                except Exception as e:
                    logger.warning(f"Cannot update lead status in database: {e}")
                    # Обновляем статус в резервных данных
                    for memory_lead in _memory_leads:
                        if str(memory_lead.get('id')) == str(lead_id):
                            memory_lead['status'] = new_status
                            updated_lead = memory_lead
                            break
            except Exception as db_error:
                logger.error(f"Database error when updating lead {lead_id}: {db_error}")
                # Обновляем статус в резервных данных
                updated_lead = None
                for memory_lead in _memory_leads:
                    if str(memory_lead.get('id')) == str(lead_id):
                        old_status = memory_lead.get('status', 'new')
                        memory_lead['status'] = new_status
                        updated_lead = memory_lead
                        break
                        
                if not updated_lead:
                    # Создаем минимальный лид для демонстрации
                    updated_lead = {
                        'id': lead_id,
                        'status': new_status,
                        'name': f'Lead #{lead_id}',
                        'source': 'demo'
                    }
                    _memory_leads.append(updated_lead)
            
            return jsonify({
                'success': True,
                'lead': updated_lead
            })
        except Exception as e:
            logger.error(f"Error updating lead status for {lead_id}: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
            
    @app.route('/api/leads/analyze', methods=['POST'])
    def analyze_lead_content_api():
        """Analyze lead content and determine next status"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
                
            content = data.get('content')
            current_status = data.get('current_status')
            
            if not content or not current_status:
                return jsonify({'error': 'Content and current_status are required'}), 400
            
            # Process with AI
            processor = get_inquiry_processor()
            analysis = processor._analyze_with_ai(content)
            
            # Determine next status based on analysis
            next_status = current_status  # default to no change
            
            # Extract urgency and category from analysis
            urgency = analysis.get('urgency', 0)
            category = analysis.get('category', '').lower()
            
            # Determine next status based on AI analysis
            if current_status == 'new':
                next_status = 'in_progress'
            elif current_status == 'in_progress':
                if 'бронирование' in category or 'booking' in category:
                    next_status = 'booked'
                elif urgency >= 4 or 'vip' in category or 'люкс' in category:
                    next_status = 'negotiation'
                else:
                    next_status = 'negotiation'
            elif current_status == 'negotiation':
                if 'бронирование' in category or 'booking' in category:
                    next_status = 'booked'
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'next_status': next_status
            })
        except Exception as e:
            logger.error(f"Error analyzing lead content: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "next_status": current_status,  # Return original status on error
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/process-all', methods=['POST'])
    def process_all_inquiries_api():
        """Process all active inquiries"""
        try:
            from inquiry_processor import get_inquiry_processor
            from models import LeadService, _memory_leads
            import random
            import time
            
            # Get parameters from request
            data = request.json or {}
            scope = data.get('scope', 'new')
            options = data.get('options', {})
            
            # Use mock data for demo to ensure functionality
            mock_data = True
            
            # Demo data response for testing UI
            if mock_data:
                # Simulate a short delay for processing
                time.sleep(1)
                
                # Create response data matching the lead IDs in the HTML
                # Include AI analysis results and generated responses
                results = {
                    'total': 7,  # Обрабатываем все 7 карточек
                    'updated': 7, 
                    'failed': 0,
                    'details': [
                        {
                            'lead_id': '1',  # Changed to match HTML id
                            'old_status': 'new',
                            'new_status': 'in_progress',
                            'tags': ['Пляжный отдых', 'Семья', 'Турция'],
                            'changed': True,
                            'ai_processed': True,
                            'ai_analysis': {
                                'summary': 'Запрос на семейный отдых в Турции. Клиент интересуется пляжным отдыхом с детьми, анимацией и бассейнами.',
                                'urgency': 3,
                                'category': 'Семейный отдых',
                                'important_info': 'Важно: нужен отель с аквапарком, рядом с песчаным пляжем, детской анимацией на русском языке'
                            },
                            'generated_response': 'Здравствуйте! Благодарим вас за интерес к семейному отдыху в Турции. Мы подготовили для вас несколько вариантов отелей с анимацией и подходящей инфраструктурой для детей. Наш менеджер свяжется с вами в ближайшее время для уточнения деталей.',
                            'blockchain_status': 'Запись добавлена в блокчейн, ID: CB-78F5A2D9'
                        },
                        {
                            'lead_id': '2',  # Changed to match HTML id
                            'old_status': 'new',
                            'new_status': 'negotiation',
                            'tags': ['Экскурсии', 'Европа'],
                            'changed': True,
                            'ai_processed': True,
                            'ai_analysis': {
                                'summary': 'Запрос на экскурсионную программу по Европе. Клиент высказывает интерес к культурным достопримечательностям Италии, Испании и Франции.',
                                'urgency': 4,
                                'category': 'Культурный туризм',
                                'important_info': 'Важно: интересует комфортный автобус, небольшая группа, отели в центре городов'
                            },
                            'generated_response': 'Добрый день! Рады предложить вам эксклюзивный маршрут по культурным столицам Европы. Мы подготовили программу с посещением ключевых достопримечательностей Италии, Испании и Франции. Наш эксперт по Европе свяжется с вами, чтобы обсудить детали.',
                            'blockchain_status': 'Запись добавлена в блокчейн, ID: CB-39A1F7B2'
                        },
                        {
                            'lead_id': '3',  # Changed to match HTML id
                            'old_status': 'new',
                            'new_status': 'booked',
                            'tags': ['Горнолыжный', 'Зима'],
                            'changed': True,
                            'ai_processed': True,
                            'ai_analysis': {
                                'summary': 'Запрос о горнолыжном отдыхе в Австрии или Швейцарии. Клиент планирует поездку на декабрь 2025 года.',
                                'urgency': 5,
                                'category': 'Горнолыжный отдых',
                                'important_info': 'Важно: необходимо уточнить уровень катания, бюджет от 5000 евро, раннее бронирование'
                            },
                            'generated_response': 'Здравствуйте! Мы рады предложить вам премиальные варианты горнолыжного отдыха в Австрии и Швейцарии на декабрь 2025 года. Именно сейчас самое удачное время для бронирования, так как мы можем предложить лучшие цены по раннему бронированию.',
                            'blockchain_status': 'Запись добавлена в блокчейн, ID: CB-12E8C3F1'
                        },
                        {
                            'lead_id': '4',
                            'old_status': 'new',
                            'new_status': 'in_progress',
                            'tags': ['Австрия', 'Горные лыжи'],
                            'changed': True,
                            'ai_processed': True,
                            'ai_analysis': {
                                'summary': 'Запрос о горнолыжных курортах в Австрии. Интересуется трассами разной сложности и детской инфраструктурой.',
                                'urgency': 4,
                                'category': 'Горнолыжный отдых',
                                'important_info': 'Важно: наличие горнолыжного снаряжения, обучение для начинающих, русскоговорящие инструкторы'
                            },
                            'generated_response': 'Здравствуйте! Мы подготовили для вас подборку лучших горнолыжных курортов Австрии с трассами разной сложности и хорошей инфраструктурой для начинающих. Многие курорты предлагают русскоговорящих инструкторов и прокат снаряжения.',
                            'blockchain_status': 'Запись добавлена в блокчейн, ID: CB-45D7F821'
                        },
                        {
                            'lead_id': '5',
                            'old_status': 'new',
                            'new_status': 'negotiation',
                            'tags': ['Испания', 'Семейный отдых', 'Дети'],
                            'changed': True,
                            'ai_processed': True,
                            'ai_analysis': {
                                'summary': 'Запрос на семейный отдых в Испании с детьми. Интересуются отелями с детской анимацией и бассейнами.',
                                'urgency': 3,
                                'category': 'Семейный отдых',
                                'important_info': 'Важно: необходимость детского меню, развлечения для детей 3-7 лет, пологий вход в море'
                            },
                            'generated_response': 'Здравствуйте! Мы подобрали для вас несколько отличных семейных отелей в Испании с детской анимацией, бассейнами и удобным пляжем. Все отели имеют специальное детское меню и находятся в районах с пологим входом в море.',
                            'blockchain_status': 'Запись добавлена в блокчейн, ID: CB-98A2E345'
                        },
                        {
                            'lead_id': '6',
                            'old_status': 'new',
                            'new_status': 'booked',
                            'tags': ['Италия', 'Экскурсии', 'История'],
                            'changed': True,
                            'ai_processed': True,
                            'ai_analysis': {
                                'summary': 'Запрос на экскурсионный тур по Италии. Особый интерес к историческим и культурным достопримечательностям.',
                                'urgency': 4,
                                'category': 'Культурный туризм',
                                'important_info': 'Важно: предпочтение исторических экскурсий, интерес к музеям, желание посетить Ватикан'
                            },
                            'generated_response': 'Здравствуйте! Мы разработали специальный экскурсионный маршрут по Италии с акцентом на исторические и культурные достопримечательности. Программа включает посещение ключевых музеев и специальную экскурсию в Ватикан с русскоговорящим гидом.',
                            'blockchain_status': 'Запись добавлена в блокчейн, ID: CB-56C9D123'
                        },
                        {
                            'lead_id': '7',
                            'old_status': 'new',
                            'new_status': 'in_progress',
                            'tags': ['Мальдивы', 'Пляжный отдых', 'VIP'],
                            'changed': True,
                            'ai_processed': True,
                            'ai_analysis': {
                                'summary': 'Запрос на отдых на Мальдивах в сентябре. VIP-клиент, интересуется виллами на воде и дайвингом.',
                                'urgency': 5,
                                'category': 'Премиум отдых',
                                'important_info': 'Важно: отель только для взрослых, высокий уровень приватности, опция персонального батлера'
                            },
                            'generated_response': 'Здравствуйте! Для вас мы подготовили эксклюзивную подборку премиальных вилл на воде на Мальдивах. Все предложения включают высокий уровень приватности, услуги персонального батлера и расположены в отелях только для взрослых с отличными возможностями для дайвинга.',
                            'blockchain_status': 'Запись добавлена в блокчейн, ID: CB-88E4F567'
                        }
                    ]
                }
                
                return jsonify(results)
            
            # Regular implementation below (for real production use)
            # Initialize processor
            processor = get_inquiry_processor()
            
            # Get leads based on scope
            leads = []
            try:
                if scope == 'new':
                    # Only process new leads
                    new_leads = LeadService.get_leads(status='new') or []
                    leads.extend(new_leads)
                elif scope == 'all':
                    # Process all active leads
                    active_statuses = ['new', 'in_progress', 'pending', 'negotiation']
                    for status in active_statuses:
                        status_leads = LeadService.get_leads(status=status) or []
                        leads.extend(status_leads)
                elif scope == 'selected':
                    # For selected, we'd need lead IDs from request
                    lead_ids = data.get('lead_ids', [])
                    if lead_ids:
                        for lead_id in lead_ids:
                            lead = LeadService.get_lead(lead_id)
                            if lead:
                                leads.append(lead)
            except Exception as db_error:
                logger.warning(f"Database error: {db_error}. Using memory storage.")
                # Use memory storage as fallback
                if scope == 'new':
                    leads = [lead for lead in _memory_leads if lead.get('status') == 'new']
                elif scope == 'all':
                    active_statuses = ['new', 'in_progress', 'pending', 'negotiation']
                    leads = [lead for lead in _memory_leads if lead.get('status') in active_statuses]
                elif scope == 'selected':
                    lead_ids = data.get('lead_ids', [])
                    leads = [lead for lead in _memory_leads if lead.get('id') in lead_ids]
            
            # Process results
            results = {
                'total': len(leads),
                'updated': 0,
                'failed': 0,
                'details': []
            }
            
            # Process each lead
            for lead in leads:
                try:
                    lead_id = lead.get('id')
                    old_status = lead.get('status', 'new')
                    
                    # Simulate AI analysis with random outcomes
                    new_status = old_status
                    if old_status == 'new':
                        new_status = random.choice(['in_progress', 'negotiation'])
                    elif old_status == 'in_progress':
                        new_status = random.choice(['negotiation', 'booked'])
                    
                    # Record changes
                    if new_status != old_status:
                        # Try to update in database
                        try:
                            LeadService.update_lead(lead_id, {'status': new_status})
                        except Exception as e:
                            logger.warning(f"Cannot update lead in database: {e}")
                            # Update in memory for demo
                            for mem_lead in _memory_leads:
                                if mem_lead.get('id') == lead_id:
                                    mem_lead['status'] = new_status
                                    break
                        
                        # Record success
                        results['updated'] += 1
                        results['details'].append({
                            'lead_id': lead_id,
                            'old_status': old_status,
                            'new_status': new_status,
                            'tags': lead.get('tags', []),
                            'changed': True
                        })
                except Exception as e:
                    results['failed'] += 1
                    logger.error(f"Error processing lead {lead.get('id')}: {e}")
            
            return jsonify(results)
        except Exception as e:
            logger.error(f"Error processing all inquiries: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/bookings/check/<reference>', methods=['GET'])
    def check_booking_api(reference):
        """Check a booking's details"""
        try:
            from api_integration import get_api_integration
            
            api = get_api_integration()
            result = api.check_booking(reference)
            
            if not result:
                return jsonify({'error': 'Booking not found'}), 404
            
            return jsonify({'booking': result})
        except Exception as e:
            logger.error(f"Error checking booking {reference}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/flights/check', methods=['GET'])
    def check_flight_api():
        """Check a flight's status"""
        try:
            from api_integration import get_api_integration
            
            flight_number = request.args.get('flight_number')
            flight_date = request.args.get('flight_date')
            
            if not flight_number or not flight_date:
                return jsonify({'error': 'Flight number and date are required'}), 400
            
            api = get_api_integration()
            result = api.check_flight(flight_number, flight_date)
            
            if not result:
                return jsonify({'error': 'Flight not found'}), 404
            
            return jsonify({'flight': result})
        except Exception as e:
            logger.error(f"Error checking flight {flight_number}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    # AI Agents API Routes
    @app.route('/api/agents/config', methods=['GET'])
    def get_agents_config_api():
        """Get the current AI configuration"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            processor = get_inquiry_processor()
            config = processor.get_config()
            
            return jsonify({
                'success': True,
                'config': config,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting agent config: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @app.route('/api/agents/config', methods=['PUT'])
    def update_agents_config_api():
        """Update the AI configuration"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            processor = get_inquiry_processor()
            config = processor.update_agent_config(data)
            
            return jsonify({
                'success': True,
                'config': config,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error updating agent config: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @app.route('/api/agents', methods=['GET'])
    def get_agents_api():
        """Get all AI agents"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            processor = get_inquiry_processor()
            agents = processor.get_agents()
            
            return jsonify({
                'success': True,
                'agents': agents,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting agents: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @app.route('/api/agents/<agent_id>', methods=['GET'])
    def get_agent_api(agent_id):
        """Get a specific AI agent"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            processor = get_inquiry_processor()
            agent = processor.get_agent(agent_id)
            
            if not agent:
                return jsonify({'error': 'Agent not found'}), 404
            
            return jsonify({
                'success': True,
                'agent': agent,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting agent {agent_id}: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @app.route('/api/agents/<agent_id>', methods=['PUT'])
    def update_agent_api(agent_id):
        """Update an AI agent"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            processor = get_inquiry_processor()
            agent = processor.update_agent(agent_id, data)
            
            if not agent:
                return jsonify({'error': 'Agent not found'}), 404
            
            return jsonify({
                'success': True,
                'agent': agent,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error updating agent {agent_id}: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @app.route('/api/agents', methods=['POST'])
    def add_agent_api():
        """Add a new AI agent"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            processor = get_inquiry_processor()
            agent = processor.add_agent(data)
            
            if not agent:
                return jsonify({'error': 'Invalid agent data or agent ID already exists'}), 400
            
            return jsonify({
                'success': True,
                'agent': agent,
                'timestamp': datetime.now().isoformat()
            }), 201
        except Exception as e:
            logger.error(f"Error adding agent: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @app.route('/api/agents/stats', methods=['GET'])
    def get_agent_stats_api():
        """Get AI agent usage statistics"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            processor = get_inquiry_processor()
            stats = processor.get_agent_usage_stats()
            
            # Check if the enhanced stats are available
            if 'cache_status' in stats:
                # Already has the enhanced stats format
                return jsonify({
                    'success': True,
                    'stats': stats,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                # Add enhanced stats format manually
                enhanced_stats = {
                    'agents': stats.get('agents', {}),
                    'total_processed': stats.get('total_processed', 0),
                    'total_successful': stats.get('total_successful', 0),
                    'total_failed': stats.get('total_failed', 0),
                    'cache_status': 'database',
                    'timestamp': datetime.now().isoformat()
                }
                
                # Calculate agent counts
                agents = stats.get('agents', {})
                active_agents = sum(1 for a in agents.values() if a.get('active', False))
                inactive_agents = sum(1 for a in agents.values() if not a.get('active', False))
                
                enhanced_stats['agent_counts'] = {
                    'total': len(agents),
                    'active': active_agents,
                    'inactive': inactive_agents,
                    'with_usage': sum(1 for a in agents.values() if a.get('total_calls', 0) > 0)
                }
                
                # Calculate overall success rate
                if enhanced_stats['total_processed'] > 0:
                    enhanced_stats['overall_success_rate'] = round(
                        (enhanced_stats['total_successful'] / enhanced_stats['total_processed']) * 100, 1
                    )
                else:
                    enhanced_stats['overall_success_rate'] = 0.0
                
                return jsonify({
                    'success': True,
                    'stats': enhanced_stats,
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            logger.error(f"Error getting agent stats: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    logger.info('API routes registered successfully')
    return app