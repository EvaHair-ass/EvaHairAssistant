// Структура отчёта: описание для модели (JSON Schema) и проверка ответа.

const str = (description) => ({ type: 'string', description });
const list = (items, min, max) => ({ type: 'array', items, minItems: min, maxItems: max });

export const REPORT_SCHEMA = {
  type: 'object',
  required: ['niche', 'audience', 'problems', 'desires', 'content', 'products'],
  properties: {
    niche: str('Название ниши с заглавной буквы, коротко, на русском'),
    audience: {
      type: 'object',
      required: ['who', 'situation', 'experience', 'life_context', 'why_follow'],
      properties: {
        who: str('Кто они: 2–3 предложения про человека, его мотивы и самоощущение'),
        situation: str('В какой ситуации находятся прямо сейчас'),
        experience: str('Какой у них уровень опыта в теме'),
        life_context: str('Что происходит в их жизни, из-за чего их зацепила эта ниша'),
        why_follow: str('Почему они подписываются на Instagram-страницу об этой теме'),
      },
    },
    problems: list(
      {
        type: 'object',
        required: ['title', 'description'],
        properties: {
          title: str('Проблема в 3–8 словах'),
          description: str('С чем именно человек борется, 1–2 предложения'),
        },
      },
      5,
      10,
    ),
    desires: list(
      {
        type: 'object',
        required: ['title', 'description'],
        properties: {
          title: str('Желаемый результат в 3–8 словах'),
          description: str('Как это выглядит именно в этой нише, 1–2 предложения'),
        },
      },
      5,
      10,
    ),
    content: list(
      {
        type: 'object',
        required: ['category', 'ideas'],
        properties: {
          category: str('Название контентной категории'),
          ideas: list(str('Хук или заголовок поста для Instagram'), 3, 3),
        },
      },
      5,
      8,
    ),
    products: list(
      {
        type: 'object',
        required: ['name', 'helps', 'description'],
        properties: {
          name: str('Название или концепция продукта'),
          helps: str('Какую проблему или желание закрывает'),
          description: str('Одно предложение: что внутри'),
        },
      },
      5,
      10,
    ),
  },
};

const clean = (v, max = 600) => (typeof v === 'string' ? v.trim().slice(0, max) : '');

function takeList(value, min, max, mapItem, label) {
  if (!Array.isArray(value)) throw new Error(`Нет раздела: ${label}`);
  const items = value.map(mapItem).filter(Boolean).slice(0, max);
  if (items.length < min) throw new Error(`Слишком мало пунктов в разделе: ${label}`);
  return items;
}

const titled = (item) => {
  const title = clean(item?.title, 160);
  const description = clean(item?.description);
  return title && description ? { title, description } : null;
};

/** Приводит ответ модели (или тело запроса на сохранение) к строгому виду. Бросает Error с понятным текстом. */
export function normalizeReport(raw) {
  if (!raw || typeof raw !== 'object') throw new Error('Пустой отчёт');
  const a = raw.audience ?? {};
  const audience = {
    who: clean(a.who),
    situation: clean(a.situation),
    experience: clean(a.experience),
    life_context: clean(a.life_context),
    why_follow: clean(a.why_follow),
  };
  if (Object.values(audience).some((v) => !v)) throw new Error('Раздел «На кого мы ориентируемся» неполный');

  const niche = clean(raw.niche, 100);
  if (!niche) throw new Error('Нет названия ниши');

  return {
    niche,
    audience,
    problems: takeList(raw.problems, 5, 10, titled, 'проблемы'),
    desires: takeList(raw.desires, 5, 10, titled, 'желания'),
    content: takeList(
      raw.content,
      5,
      8,
      (c) => {
        const category = clean(c?.category, 120);
        const ideas = Array.isArray(c?.ideas) ? c.ideas.map((i) => clean(i, 300)).filter(Boolean).slice(0, 3) : [];
        return category && ideas.length === 3 ? { category, ideas } : null;
      },
      'контент',
    ),
    products: takeList(
      raw.products,
      5,
      10,
      (p) => {
        const name = clean(p?.name, 160);
        const helps = clean(p?.helps);
        const description = clean(p?.description);
        return name && helps && description ? { name, helps, description } : null;
      },
      'продукты',
    ),
  };
}
