const navLinks = [...document.querySelectorAll('.primary-nav a[href^="#"]')];
const sections = navLinks
  .map((link) => document.querySelector(link.getAttribute('href')))
  .filter(Boolean);
const progress = document.querySelector('.reading-progress span');
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

document.documentElement.classList.add('js-ready');

const scenarioForm = document.querySelector('#bestseller-form');
const scenarioOutput = document.querySelector('#scenario-output');
if (scenarioForm && scenarioOutput) {
  scenarioForm.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!scenarioForm.reportValidity()) return;
    const values = new FormData(scenarioForm);
    const price = Number(values.get('price'));
    const discount = Number(values.get('discount'));
    const installment = values.get('installment') === 'yes' ? 'available' : 'not available';
    scenarioOutput.replaceChildren();
    const label = document.createElement('p');
    label.className = 'ai-output__label';
    label.textContent = 'Scenario reviewed · no prediction';
    const summary = document.createElement('p');
    summary.textContent = `Input snapshot: ${new Intl.NumberFormat('en-US').format(price)} UZS, ${discount}% discount, installment ${installment}. These values alone do not satisfy the trained model’s complete feature schema, so no probability is calculated.`;
    scenarioOutput.append(label, summary);
  });
}

const recommendationSelect = document.querySelector('#recommendation-product');
const recommendationOutput = document.querySelector('#recommendation-output');
const recommendationData = window.aiLabRecommendationExamples;
if (recommendationSelect && recommendationOutput && recommendationData?.products?.length) {
  const money = new Intl.NumberFormat('en-US');
  recommendationSelect.replaceChildren(new Option('Choose a starting product', ''));
  recommendationData.products.forEach((product, index) => {
    recommendationSelect.add(new Option(`${product.title} · ${product.category}`, String(index)));
  });
  recommendationOutput.setAttribute('aria-busy', 'false');
  recommendationSelect.addEventListener('change', () => {
    const product = recommendationData.products[Number(recommendationSelect.value)];
    recommendationOutput.replaceChildren();
    if (!product) {
      const empty = document.createElement('p');
      empty.textContent = 'Choose a starting product to inspect its precomputed recommendations.';
      recommendationOutput.append(empty);
      return;
    }
    const source = document.createElement('p');
    source.className = 'recommendation-output__source';
    source.textContent = `For “${product.title}” · ${product.category} · ${money.format(product.price)} UZS`;
    const list = document.createElement('ol');
    product.recommendations.forEach((item) => {
      const row = document.createElement('li');
      const details = document.createElement('span');
      details.className = 'recommendation-output__details';
      details.textContent = `${item.category} · ${money.format(item.price)} UZS`;
      const score = document.createElement('span');
      score.className = 'recommendation-output__score';
      score.textContent = `Source match score ${item.score.toFixed(3)}`;
      row.append(document.createTextNode(item.title), details, score);
      list.append(row);
    });
    recommendationOutput.append(source, list);
  });
} else if (recommendationSelect && recommendationOutput) {
  recommendationSelect.replaceChildren(new Option('Examples unavailable', ''));
  recommendationSelect.disabled = true;
  recommendationOutput.setAttribute('aria-busy', 'false');
  recommendationOutput.textContent = 'The precomputed example file did not load. Reload the page from the project website directory.';
}

const revealTargets = document.querySelectorAll(
  '.intro-band__body, .facts-ledger, .source-note, .engineering-grid article, .feature-figure, .experiment-list article, .limits-grid article, .resource-entry'
);

if ('IntersectionObserver' in window && !reduceMotion) {
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -24px 0px' });

  revealTargets.forEach((element) => {
    element.classList.add('reveal');
    revealObserver.observe(element);
  });

  const workflow = document.querySelector('.workflow-sketch');
  if (workflow) {
    const workflowObserver = new IntersectionObserver((entries, observer) => {
      if (entries.some((entry) => entry.isIntersecting)) {
        workflow.classList.add('is-visible');
        observer.disconnect();
      }
    }, { threshold: 0.25 });
    workflowObserver.observe(workflow);
  }
}

if ('IntersectionObserver' in window) {
  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const active = `#${entry.target.id}`;
      navLinks.forEach((link) => {
        if (link.getAttribute('href') === active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    });
  }, { rootMargin: '-25% 0px -65% 0px' });
  sections.forEach((section) => sectionObserver.observe(section));
}

let ticking = false;
const updateProgress = () => {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const ratio = scrollable > 0 ? window.scrollY / scrollable : 0;
  if (progress) progress.style.transform = `scaleX(${Math.min(1, Math.max(0, ratio))})`;
  ticking = false;
};

window.addEventListener('scroll', () => {
  if (!ticking) {
    window.requestAnimationFrame(updateProgress);
    ticking = true;
  }
}, { passive: true });

updateProgress();
